<?php
defined('BASEPATH') OR exit('No direct script access allowed');

class CI_Output {
	public $final_output = '';
	public $headers = array();
	public $status_code = 200;

	public function set_output($output) {
		$this->final_output = $output;
		return $this;
	}

	public function get_output() {
		return $this->final_output;
	}

	public function append_output($output) {
		$this->final_output .= $output;
		return $this;
	}

	public function set_content_type($mime_type, $charset = NULL) {
		if ($mime_type === 'application/json') {
			$header = 'Content-Type: application/json; charset=' . ($charset ?: 'UTF-8');
		} else {
			$header = 'Content-Type: ' . $mime_type;
		}
		$this->headers[] = array($header, TRUE);
		return $this;
	}

	public function set_status_header($code = 200, $text = '') {
		$this->status_code = $code;
		set_status_header($code, $text);
		return $this;
	}

	public function _display($output = '') {
		if ($output === '') {
			$output = $this->final_output;
		}
		foreach ($this->headers as $header) {
			header($header[0], $header[1]);
		}
		echo $output;
	}
}
