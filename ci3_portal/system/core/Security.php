<?php
defined('BASEPATH') OR exit('No direct script access allowed');

class CI_Security {
	protected $_csrf_hash;
	protected $_csrf_expire;
	protected $_csrf_token_name;
	protected $_csrf_cookie_name;

	public function __construct() {
		$this->_csrf_expire = config_item('csrf_expire') ?: 7200;
		$this->_csrf_token_name = config_item('csrf_token_name') ?: 'atlas_csrf_token';
		$this->_csrf_cookie_name = config_item('csrf_cookie_name') ?: 'atlas_csrf_cookie';

		if (config_item('csrf_protection') === TRUE) {
			$this->csrf_set_hash();
		}
	}

	public function csrf_verify() {
		if (strtoupper($_SERVER['REQUEST_METHOD']) !== 'POST') {
			return $this;
		}

		if ( ! isset($_POST[$this->_csrf_token_name], $_COOKIE[$this->_csrf_cookie_name])
			OR $_POST[$this->_csrf_token_name] !== $_COOKIE[$this->_csrf_cookie_name])
		{
			$this->csrf_show_error();
		}

		return $this;
	}

	public function csrf_set_hash() {
		if ( ! empty($_COOKIE[$this->_csrf_cookie_name])) {
			$this->_csrf_hash = $_COOKIE[$this->_csrf_cookie_name];
		} else {
			$this->_csrf_hash = bin2hex(random_bytes(16));
			setcookie(
				$this->_csrf_cookie_name,
				$this->_csrf_hash,
				time() + $this->_csrf_expire,
				config_item('cookie_path') ?: '/',
				config_item('cookie_domain') ?: '',
				config_item('cookie_secure') ?: FALSE,
				config_item('cookie_httponly') ?: FALSE
			);
		}
		return $this->_csrf_hash;
	}

	public function get_csrf_hash() {
		return $this->_csrf_hash;
	}

	public function get_csrf_token_name() {
		return $this->_csrf_token_name;
	}

	public function csrf_show_error() {
		show_error('The action you have requested is not allowed. CSRF verification failed.', 403);
	}

	public function xss_clean($str, $is_image = FALSE) {
		if (is_array($str)) {
			foreach ($str as $key => $val) {
				$str[$key] = $this->xss_clean($val, $is_image);
			}
			return $str;
		}
		return htmlspecialchars($str, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
	}
}
