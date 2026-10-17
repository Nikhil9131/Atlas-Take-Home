<?php
defined('BASEPATH') OR exit('No direct script access allowed');

class CI_Input {
	protected $security;

	public function __construct() {
		$this->security =& load_class('Security', 'core');
	}

	public function get($index = NULL, $xss_clean = NULL) {
		return $this->_fetch_from_array($_GET, $index, $xss_clean);
	}

	public function post($index = NULL, $xss_clean = NULL) {
		return $this->_fetch_from_array($_POST, $index, $xss_clean);
	}

	public function post_get($index, $xss_clean = NULL) {
		return isset($_POST[$index])
			? $this->post($index, $xss_clean)
			: $this->get($index, $xss_clean);
	}

	public function cookie($index = NULL, $xss_clean = NULL) {
		return $this->_fetch_from_array($_COOKIE, $index, $xss_clean);
	}

	public function server($index, $xss_clean = NULL) {
		return $this->_fetch_from_array($_SERVER, $index, $xss_clean);
	}

	public function method($upper = FALSE) {
		return ($upper)
			? strtoupper($this->server('REQUEST_METHOD'))
			: strtolower($this->server('REQUEST_METHOD'));
	}

	public function is_ajax_request() {
		return (!empty($_SERVER['HTTP_X_REQUESTED_WITH']) && strtolower($_SERVER['HTTP_X_REQUESTED_WITH']) === 'xmlhttprequest');
	}

	protected function _fetch_from_array(&$array, $index = NULL, $xss_clean = NULL) {
		$is_xss_clean = ($xss_clean === NULL) ? config_item('global_xss_filtering') : $xss_clean;

		if ($index === NULL) {
			$output = array();
			foreach (array_keys($array) as $key) {
				$output[$key] = $this->_fetch_from_array($array, $key, $is_xss_clean);
			}
			return $output;
		}

		if (isset($array[$index])) {
			$value = $array[$index];
		} elseif (($count = preg_match_all('/(?:^[^\[]+)|\[[^]]*\]/', $index, $matches)) > 1) {
			$value = $array;
			for ($i = 0; $i < $count; $i++) {
				$key = trim($matches[0][$i], '[]');
				if ($key === '') {
					break;
				}
				if (isset($value[$key])) {
					$value = $value[$key];
				} else {
					return NULL;
				}
			}
		} else {
			return NULL;
		}

		return ($is_xss_clean === TRUE) ? $this->security->xss_clean($value) : $value;
	}
}
