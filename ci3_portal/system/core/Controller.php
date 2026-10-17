<?php
defined('BASEPATH') OR exit('No direct script access allowed');

#[AllowDynamicProperties]
class CI_Controller {
	private static $instance;
	public $load;

	public function __construct() {
		self::$instance =& $this;

		foreach (is_loaded() as $var => $class) {
			$this->$var =& load_class($class);
		}

		$this->load =& load_class('Loader', 'core');

		// Autoload helpers & libraries
		if (file_exists(APPPATH.'config/autoload.php')) {
			include(APPPATH.'config/autoload.php');
			if (!empty($autoload['helper'])) {
				$this->load->helper($autoload['helper']);
			}
			if (!empty($autoload['libraries'])) {
				$this->load->library($autoload['libraries']);
			}
		}
	}

	public static function &get_instance() {
		return self::$instance;
	}
}
