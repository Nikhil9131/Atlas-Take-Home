<?php
defined('BASEPATH') OR exit('No direct script access allowed');

/**
 * Fastapi_client Library
 * Facilitates robust, authenticated HTTP communication between legacy CodeIgniter 3
 * and the Project Atlas Python FastAPI service.
 */
class Fastapi_client {

    protected $CI;
    protected $api_base_url;
    protected $api_key;
    protected $timeout_seconds;

    public function __construct() {
        $this->CI =& get_instance();
        
        // Environment configuration with sensible local and docker container fallbacks
        $this->api_base_url = rtrim(getenv('FASTAPI_URL') ?: 'http://127.0.0.1:8000', '/');
        $this->api_key = getenv('API_KEY') ?: 'atlas-secret-key-2025';
        $this->timeout_seconds = (int)(getenv('FASTAPI_TIMEOUT') ?: 30);
    }

    /**
     * Send chat inquiry to FastAPI backend.
     * 
     * @param array $data ['client_id' => ..., 'question' => ..., 'conversation_id' => ...]
     * @return array ['success' => bool, 'data' => ..., 'error' => ...]
     */
    public function send_chat($data) {
        $url = $this->api_base_url . '/chat';
        return $this->_make_request('POST', $url, $data);
    }

    /**
     * Fetch paginated escalation tickets.
     */
    public function get_escalations($client_id = null, $page = 1, $limit = 20) {
        $query_params = array('page' => $page, 'limit' => $limit);
        if (!empty($client_id)) {
            $query_params['client_id'] = $client_id;
        }
        $url = $this->api_base_url . '/escalations?' . http_build_query($query_params);
        return $this->_make_request('GET', $url);
    }

    /**
     * Submit user feedback (thumbs up / thumbs down).
     */
    public function send_feedback($data) {
        $url = $this->api_base_url . '/feedback';
        return $this->_make_request('POST', $url, $data);
    }

    /**
     * Check backend health and readiness.
     */
    public function get_health() {
        $url = $this->api_base_url . '/health';
        return $this->_make_request('GET', $url);
    }

    /**
     * Internal cURL request dispatcher with explicit timeouts, headers, and error handling.
     */
    protected function _make_request($method, $url, $payload = null) {
        $ch = curl_init();
        
        $headers = array(
            'Content-Type: application/json',
            'Accept: application/json',
            'X-API-Key: ' . $this->api_key,
            'X-Request-Source: CI3-Legacy-Portal'
        );

        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);
        curl_setopt($ch, CURLOPT_TIMEOUT, $this->timeout_seconds);
        curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, FALSE);

        if (strtoupper($method) === 'POST') {
            curl_setopt($ch, CURLOPT_POST, TRUE);
            if ($payload !== null) {
                curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));
            }
        }

        $raw_response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $curl_error_num = curl_errno($ch);
        $curl_error_msg = curl_error($ch);
        curl_close($ch);

        if ($curl_error_num !== 0) {
            log_message('error', 'FastAPI communication error: ' . $curl_error_msg . ' (' . $url . ')');
            return array(
                'success' => FALSE,
                'http_code' => 0,
                'error' => 'The Research Copilot service is temporarily unreachable (' . $curl_error_msg . '). Please try again momentarily.',
                'data' => null
            );
        }

        $decoded_json = json_decode($raw_response, TRUE);

        if ($http_code >= 200 && $http_code < 300) {
            return array(
                'success' => TRUE,
                'http_code' => $http_code,
                'error' => null,
                'data' => $decoded_json
            );
        } else {
            $error_detail = isset($decoded_json['detail']) ? $decoded_json['detail'] : 'Backend service returned HTTP ' . $http_code;
            log_message('error', 'FastAPI error response [' . $http_code . ']: ' . $error_detail);
            return array(
                'success' => FALSE,
                'http_code' => $http_code,
                'error' => $error_detail,
                'data' => $decoded_json
            );
        }
    }
}
