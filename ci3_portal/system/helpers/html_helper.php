<?php
defined('BASEPATH') OR exit('No direct script access allowed');

if ( ! function_exists('heading')) {
	function heading($data = '', $h = '1', $attributes = '') {
		return '<h'.$h.(is_array($attributes) ? '' : ' '.$attributes).'>'.$data.'</h'.$h.'>';
	}
}

if ( ! function_exists('br')) {
	function br($count = 1) {
		return str_repeat('<br />', $count);
	}
}
