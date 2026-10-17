<?php
defined('BASEPATH') OR exit('No direct script access allowed');

class CI_URI {
	public $uri_string = '';
	public $segments = array();

	public function __construct() {
		$uri = isset($_SERVER['REQUEST_URI']) ? $_SERVER['REQUEST_URI'] : '';
		if ($pos = strpos($uri, '?')) {
			$uri = substr($uri, 0, $pos);
		}
		// Strip index.php
		$uri = preg_replace('/^.*?index\.php\/?/', '', $uri);
		$this->uri_string = trim($uri, '/');
		
		if ($this->uri_string !== '') {
			$this->segments = explode('/', $this->uri_string);
		}
	}

	public function segment($n, $no_result = NULL) {
		return isset($this->segments[$n - 1]) ? $this->segments[$n - 1] : $no_result;
	}

	public function uri_string() {
		return $this->uri_string;
	}
}
