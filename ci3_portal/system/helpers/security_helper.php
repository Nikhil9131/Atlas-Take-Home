<?php
defined('BASEPATH') OR exit('No direct script access allowed');

if ( ! function_exists('xss_clean')) {
	function xss_clean($str, $is_image = FALSE) {
		$CI =& get_instance();
		return $CI->security->xss_clean($str, $is_image);
	}
}

if ( ! function_exists('do_hash')) {
	function do_hash($str, $type = 'sha1') {
		return hash($type, $str);
	}
}
