<?php
defined('BASEPATH') OR exit('No direct script access allowed');

/**
 * Chat Controller
 * Primary legacy web controller rendering the Research Copilot interface,
 * handling session-bound client switching, CSRF validation, and delegating queries to FastAPI.
 */
class Chat extends CI_Controller {

    public function __construct() {
        parent::__construct();
        $this->load->library('session');
        $this->load->library('fastapi_client');
        $this->load->helper(array('url', 'form', 'security', 'html'));

        // Initialize active demonstration client in session if not present
        if (!$this->session->userdata('active_client_id')) {
            $this->session->set_userdata('active_client_id', 'C-01');
            $this->session->set_userdata('active_client_name', 'Northwind Utilities');
        }
    }

    /**
     * Render the main Research Copilot interface.
     */
    public function index() {
        $client_id = $this->session->userdata('active_client_id');
        $client_name = $this->session->userdata('active_client_name');

        // Available demonstration client profiles
        $clients = array(
            'C-01' => array(
                'name' => 'Northwind Utilities',
                'entitlements' => array('R-101: Global Smart Water Meter Market 2025', 'R-103: Residential Water Purifier Market 2025'),
                'public_access' => array('R-102: Industry Outlook 2024 (Public Excerpt)')
            ),
            'C-02' => array(
                'name' => 'Blue Delta Infra',
                'entitlements' => array('R-103: Residential Water Purifier Market 2025'),
                'public_access' => array('R-102: Industry Outlook 2024 (Public Excerpt)'),
                'restricted' => array('R-101: Global Smart Water Meter Market 2025 (UNPURCHASED)')
            )
        );

        $data = array(
            'active_client_id' => $client_id,
            'active_client_name' => $client_name,
            'client_profiles' => $clients,
            'csrf_token_name' => $this->security->get_csrf_token_name(),
            'csrf_hash' => $this->security->get_csrf_hash()
        );

        $this->load->view('chat_view', $data);
    }

    /**
     * Switch the active client identity (C-01 vs C-02) within the secure session.
     */
    public function switch_client() {
        $target_client = $this->input->post('client_id', TRUE);
        if ($target_client === 'C-02') {
            $this->session->set_userdata('active_client_id', 'C-02');
            $this->session->set_userdata('active_client_name', 'Blue Delta Infra');
        } else {
            $this->session->set_userdata('active_client_id', 'C-01');
            $this->session->set_userdata('active_client_name', 'Northwind Utilities');
        }

        // Reset conversation ID on client switch
        $this->session->unset_userdata('conversation_id');

        if ($this->input->is_ajax_request()) {
            return $this->output
                ->set_content_type('application/json')
                ->set_output(json_encode(array(
                    'success' => TRUE,
                    'active_client_id' => $this->session->userdata('active_client_id'),
                    'active_client_name' => $this->session->userdata('active_client_name'),
                    'csrf_hash' => $this->security->get_csrf_hash()
                )));
        }

        redirect('chat');
    }

    /**
     * Submit user question to the AI Copilot.
     * Enforces server-side validation and session client binding.
     */
    public function send() {
        if (!$this->input->is_ajax_request() && $this->input->method() !== 'post') {
            show_404();
            return;
        }

        $question = trim($this->input->post('question', TRUE));
        if (empty($question)) {
            return $this->_json_error('Please enter a research question.');
        }

        if (mb_strlen($question) > 2000) {
            return $this->_json_error('Question exceeds maximum permitted length of 2000 characters.');
        }

        // SECURITY: Bind client identity to SESSION, never trust form-submitted client_id
        $client_id = $this->session->userdata('active_client_id');
        $conversation_id = $this->session->userdata('conversation_id');

        $payload = array(
            'client_id' => $client_id,
            'question' => $question,
            'conversation_id' => $conversation_id
        );

        $api_result = $this->fastapi_client->send_chat($payload);

        if (!$api_result['success']) {
            return $this->_json_error($api_result['error'], 502);
        }

        $response_data = $api_result['data'];

        // Save conversation ID to session for persistent dialog continuity
        if (!empty($response_data['conversation_id'])) {
            $this->session->set_userdata('conversation_id', $response_data['conversation_id']);
        }

        return $this->output
            ->set_content_type('application/json')
            ->set_output(json_encode(array(
                'success' => TRUE,
                'data' => $response_data,
                'csrf_hash' => $this->security->get_csrf_hash()
            )));
    }

    /**
     * Record thumbs up / thumbs down feedback.
     */
    public function feedback() {
        if (!$this->input->is_ajax_request()) {
            show_404();
            return;
        }

        $message_id = $this->input->post('message_id', TRUE);
        $rating = (int)$this->input->post('rating', TRUE);
        $feedback_text = $this->input->post('feedback_text', TRUE);
        $client_id = $this->session->userdata('active_client_id');

        if (empty($message_id) || !in_array($rating, array(-1, 1))) {
            return $this->_json_error('Invalid feedback payload.');
        }

        $payload = array(
            'message_id' => $message_id,
            'client_id' => $client_id,
            'rating' => $rating,
            'feedback_text' => $feedback_text
        );

        $api_result = $this->fastapi_client->send_feedback($payload);

        return $this->output
            ->set_content_type('application/json')
            ->set_output(json_encode(array(
                'success' => $api_result['success'],
                'csrf_hash' => $this->security->get_csrf_hash()
            )));
    }

    /**
     * Health check endpoint.
     */
    public function health() {
        $backend_health = $this->fastapi_client->get_health();
        return $this->output
            ->set_content_type('application/json')
            ->set_output(json_encode(array(
                'portal' => 'healthy',
                'framework' => 'CodeIgniter 3',
                'active_client' => $this->session->userdata('active_client_id'),
                'backend' => $backend_health['data']
            )));
    }

    protected function _json_error($message, $status_code = 400) {
        return $this->output
            ->set_status_header($status_code)
            ->set_content_type('application/json')
            ->set_output(json_encode(array(
                'success' => FALSE,
                'error' => html_escape($message),
                'csrf_hash' => $this->security->get_csrf_hash()
            )));
    }
}
