<?php
defined('BASEPATH') OR exit('No direct script access allowed');

/**
 * Escalations Controller
 * Allows analysts and client administrators to inspect escalated inquiries,
 * reason for escalation, and underlying confidence ratings.
 */
class Escalations extends CI_Controller {

    public function __construct() {
        parent::__construct();
        $this->load->library('session');
        $this->load->library('fastapi_client');
        $this->load->helper(array('url', 'html', 'security'));
    }

    public function index() {
        $client_id = $this->session->userdata('active_client_id');
        $api_res = $this->fastapi_client->get_escalations($client_id, 1, 50);

        $data = array(
            'escalations' => $api_res['success'] ? $api_res['data'] : array(),
            'active_client_id' => $client_id,
            'active_client_name' => $this->session->userdata('active_client_name')
        );

        $this->load->view('escalations_view', $data);
    }
}
