<?php
defined('BASEPATH') OR exit('No direct script access allowed');

if ( ! function_exists('is_php'))
{
	function is_php($version)
	{
		static $_is_php;
		$version = (string) $version;
		if ( ! isset($_is_php[$version]))
		{
			$_is_php[$version] = version_compare(PHP_VERSION, $version, '>=');
		}
		return $_is_php[$version];
	}
}

if ( ! function_exists('load_class'))
{
	function &load_class($class, $directory = 'libraries', $param = NULL)
	{
		static $_classes = array();

		if (isset($_classes[$class]))
		{
			return $_classes[$class];
		}

		$name = FALSE;

		foreach (array(APPPATH, BASEPATH) as $path)
		{
			if (file_exists($path.$directory.'/'.$class.'.php'))
			{
				if (class_exists('CI_'.$class, FALSE) === FALSE && class_exists($class, FALSE) === FALSE)
				{
					require_once($path.$directory.'/'.$class.'.php');
				}
				$name = class_exists('CI_'.$class, FALSE) ? 'CI_'.$class : $class;
				break;
			}
		}

		if ($name === FALSE)
		{
			set_status_header(503);
			echo 'Unable to locate the specified class: '.$class.'.php';
			exit(5);
		}

		is_loaded($class);

		$_classes[$class] = isset($param)
			? new $name($param)
			: new $name();
		return $_classes[$class];
	}
}

if ( ! function_exists('is_loaded'))
{
	function &is_loaded($class = '')
	{
		static $_is_loaded = array();

		if ($class !== '')
		{
			$_is_loaded[strtolower($class)] = $class;
		}

		return $_is_loaded;
	}
}

if ( ! function_exists('get_config'))
{
	function &get_config(Array $replace = array())
	{
		static $config;

		if (empty($config))
		{
			$file_path = APPPATH.'config/config.php';
			if ( ! file_exists($file_path))
			{
				set_status_header(503);
				echo 'The configuration file does not exist.';
				exit(3);
			}

			require($file_path);

			if ( ! isset($config) OR ! is_array($config))
			{
				set_status_header(503);
				echo 'Your config file does not appear to be formatted correctly.';
				exit(3);
			}
		}

		foreach ($replace as $key => $val)
		{
			$config[$key] = $val;
		}

		return $config;
	}
}

if ( ! function_exists('config_item'))
{
	function config_item($item)
	{
		static $_config;

		if (empty($_config))
		{
			$_config =& get_config();
		}

		return isset($_config[$item]) ? $_config[$item] : NULL;
	}
}

if ( ! function_exists('get_instance'))
{
	function &get_instance()
	{
		return CI_Controller::get_instance();
	}
}

if ( ! function_exists('html_escape'))
{
	function html_escape($var, $double_encode = TRUE)
	{
		if (empty($var))
		{
			return $var;
		}

		if (is_array($var))
		{
			foreach (array_keys($var) as $key)
			{
				$var[$key] = html_escape($var[$key], $double_encode);
			}
			return $var;
		}

		return htmlspecialchars($var, ENT_QUOTES | ENT_SUBSTITUTE, config_item('charset'), $double_encode);
	}
}

if ( ! function_exists('set_status_header'))
{
	function set_status_header($code = 200, $text = '')
	{
		if (is_cli())
		{
			return;
		}

		if (empty($code) OR ! is_numeric($code))
		{
			show_error('Status codes must be numeric', 500);
		}

		header('HTTP/1.1 '.$code.' '.$text, TRUE, $code);
	}
}

if ( ! function_exists('show_error'))
{
	function show_error($message, $status_code = 500, $heading = 'An Error Was Encountered')
	{
		$status_code = abs($status_code);
		if ($status_code < 100)
		{
			$exit_status = $status_code + 9;
			$status_code = 500;
		}
		else
		{
			$exit_status = 1;
		}

		set_status_header($status_code);
		echo '<h1>'.$heading.'</h1><p>'.(is_array($message) ? implode('</p><p>', $message) : $message).'</p>';
		exit($exit_status);
	}
}

if ( ! function_exists('show_404'))
{
	function show_404($page = '', $log_error = TRUE)
	{
		set_status_header(404);
		echo '<h1>404 Page Not Found</h1><p>The page you requested was not found.</p>';
		exit(4);
	}
}

if ( ! function_exists('log_message'))
{
	function log_message($level, $message)
	{
		// Basic log recording
		error_log('[CI3 '.$level.'] '.$message);
	}
}

if ( ! function_exists('is_cli'))
{
	function is_cli()
	{
		return (PHP_SAPI === 'cli' OR defined('STDIN'));
	}
}
