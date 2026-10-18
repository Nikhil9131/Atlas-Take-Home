<?php
defined('BASEPATH') OR exit('No direct script access allowed');

$route['default_controller'] = 'chat';
$route['404_override'] = '';
$route['translate_uri_dashes'] = FALSE;

$route['chat'] = 'chat/index';
$route['chat/send'] = 'chat/send';
$route['chat/switch_client'] = 'chat/switch_client';
$route['chat/feedback'] = 'chat/feedback';
$route['chat/reset'] = 'chat/reset_chat';
$route['escalations'] = 'escalations/index';
$route['health'] = 'chat/health';
