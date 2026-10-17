<?php
defined('BASEPATH') OR exit('No direct script access allowed');

if ( ! function_exists('form_open')) {
	function form_open($action = '', $attributes = array(), $hidden = array()) {
		$CI =& get_instance();
		$action = site_url($action);
		$form = '<form action="'.$action.'" method="post"';
		if (is_array($attributes)) {
			foreach ($attributes as $key => $val) {
				$form .= ' '.$key.'="'.html_escape($val).'"';
			}
		}
		$form .= '>';

		// CSRF token
		if (config_item('csrf_protection') === TRUE) {
			$form .= '<input type="hidden" name="'.$CI->security->get_csrf_token_name().'" value="'.$CI->security->get_csrf_hash().'" />';
		}

		if (is_array($hidden)) {
			foreach ($hidden as $name => $value) {
				$form .= '<input type="hidden" name="'.$name.'" value="'.html_escape($value).'" />';
			}
		}
		return $form;
	}
}

if ( ! function_exists('form_close')) {
	function form_close($extra = '') {
		return '</form>'.$extra;
	}
}
