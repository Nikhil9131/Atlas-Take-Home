<?php
defined('BASEPATH') OR exit('No direct script access allowed');

class CI_Config {
	public $config = array();
	public $is_loaded = array();
	public $_config_paths = array(APPPATH);

	public function __construct() {
		$this->config =& get_config();
		$this->is_loaded[] = 'config.php';
	}

	public function item($item, $index = '') {
		if ($index == '') {
			return isset($this->config[$item]) ? $this->config[$item] : NULL;
		}
		return isset($this->config[$index], $this->config[$index][$item]) ? $this->config[$index][$item] : NULL;
	}

	public function set_item($item, $value) {
		$this->config[$item] = $value;
	}

	public function site_url($uri = '') {
		$base_url = $this->item('base_url');
		if (empty($base_url)) {
			$base_url = (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? "https" : "http") . "://" . (isset($_SERVER['HTTP_HOST']) ? $_SERVER['HTTP_HOST'] : 'localhost') . "/";
		}
		return rtrim($base_url, '/') . '/' . ltrim($uri, '/');
	}

	public function base_url($uri = '') {
		return $this->site_url($uri);
	}
}
