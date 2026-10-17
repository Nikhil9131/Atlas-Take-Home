<?php
defined('BASEPATH') OR exit('No direct script access allowed');

class CI_Loader {
	protected $_ci_classes = array();
	protected $_ci_loaded_files = array();
	protected $_ci_models = array();
	protected $_ci_helpers = array();
	protected $_ci_varmap = array();

	public function library($library, $params = NULL, $object_name = NULL) {
		if (empty($library)) return $this;
		if (is_array($library)) {
			foreach ($library as $class) {
				$this->library($class, $params);
			}
			return $this;
		}

		$class = strtolower($library);
		$CI =& get_instance();

		if (file_exists(APPPATH.'libraries/'.ucfirst($library).'.php')) {
			require_once(APPPATH.'libraries/'.ucfirst($library).'.php');
			$class_name = ucfirst($library);
			$CI->$class = new $class_name($params);
		} elseif (file_exists(BASEPATH.'libraries/'.ucfirst($library).'.php')) {
			require_once(BASEPATH.'libraries/'.ucfirst($library).'.php');
			$class_name = 'CI_'.ucfirst($library);
			$CI->$class = new $class_name($params);
		} elseif (file_exists(BASEPATH.'libraries/'.ucfirst($library).'/'.ucfirst($library).'.php')) {
			require_once(BASEPATH.'libraries/'.ucfirst($library).'/'.ucfirst($library).'.php');
			$class_name = 'CI_'.ucfirst($library);
			$CI->$class = new $class_name($params);
		}

		return $this;
	}

	public function helper($helpers = array()) {
		if (is_string($helpers)) {
			$helpers = array($helpers);
		}
		foreach ($helpers as $helper) {
			$helper = strtolower(str_replace('_helper', '', $helper)).'_helper';
			if (file_exists(APPPATH.'helpers/'.$helper.'.php')) {
				include_once(APPPATH.'helpers/'.$helper.'.php');
			} elseif (file_exists(BASEPATH.'helpers/'.$helper.'.php')) {
				include_once(BASEPATH.'helpers/'.$helper.'.php');
			}
		}
		return $this;
	}

	public function view($view, $vars = array(), $return = FALSE) {
		$CI =& get_instance();
		foreach (get_object_vars($CI) as $_ci_key => $_ci_var) {
			if ( ! isset($this->$_ci_key)) {
				$this->$_ci_key =& $CI->$_ci_key;
			}
		}

		if (is_array($vars)) {
			extract($vars);
		}

		$view_path = VIEWPATH.$view.'.php';
		if ( ! file_exists($view_path)) {
			show_error('Unable to load the requested view: '.$view.'.php', 500);
		}

		ob_start();
		include($view_path);
		$buffer = ob_get_contents();
		ob_end_clean();

		if ($return === TRUE) {
			return $buffer;
		}

		$CI->output->append_output($buffer);
		return $this;
	}
}
