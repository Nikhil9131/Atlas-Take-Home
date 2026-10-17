<?php
defined('BASEPATH') OR exit('No direct script access allowed');

define('CI_VERSION', '3.1.13');

require_once(BASEPATH.'core/Common.php');

// Core components
$CFG =& load_class('Config', 'core');
$SEC =& load_class('Security', 'core');
$IN  =& load_class('Input', 'core');
$OUT =& load_class('Output', 'core');
$URI =& load_class('URI', 'core');
$RTR =& load_class('Router', 'core');

// Enforce CSRF verification
if (config_item('csrf_protection') === TRUE) {
	$SEC->csrf_verify();
}

// Load base controller
require_once(BASEPATH.'core/Controller.php');

$class  = ucfirst($RTR->fetch_class());
$method = $RTR->fetch_method();

// Check if controller exists
$controller_file = APPPATH.'controllers/'.$class.'.php';
if (!file_exists($controller_file)) {
	show_404();
}

require_once($controller_file);

if (!class_exists($class, FALSE) || !method_exists($class, $method)) {
	show_404();
}

$CI = new $class();
call_user_func_array(array(&$CI, $method), array());

$OUT->_display();
