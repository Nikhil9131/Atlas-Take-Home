<?php
defined('BASEPATH') OR exit('No direct script access allowed');

#[AllowDynamicProperties]
class CI_Router {
	public $uri;
	public $class = 'chat';
	public $method = 'index';
	public $routes = array();

	public function __construct($routing = NULL) {
		$this->uri =& load_class('URI', 'core');
		$this->_set_routing();
	}

	protected function _set_routing() {
		if (file_exists(APPPATH.'config/routes.php')) {
			include(APPPATH.'config/routes.php');
		}

		$this->routes = (empty($route) OR ! is_array($route)) ? array() : $route;
		$default_controller = isset($this->routes['default_controller']) ? $this->routes['default_controller'] : 'chat';

		$uri_string = $this->uri->uri_string();

		if (empty($uri_string)) {
			$this->class = $default_controller;
			$this->method = 'index';
			return;
		}

		// Check explicit route rules
		if (isset($this->routes[$uri_string])) {
			$target = explode('/', $this->routes[$uri_string]);
			$this->class = $target[0];
			$this->method = isset($target[1]) ? $target[1] : 'index';
			return;
		}

		$parts = explode('/', $uri_string);
		$this->class = !empty($parts[0]) ? strtolower($parts[0]) : $default_controller;
		$this->method = !empty($parts[1]) ? strtolower($parts[1]) : 'index';
	}

	public function fetch_class() {
		return $this->class;
	}

	public function fetch_method() {
		return $this->method;
	}
}
