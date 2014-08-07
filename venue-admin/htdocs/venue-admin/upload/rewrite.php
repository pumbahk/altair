<?php

$file = ltrim($_SERVER['PATH_INFO'], '/');

if(is_file($file)) {
	header('Content-Type: application/javascript');
	print str_replace('/cart/static/img/settlement/', '', file_get_contents($file));
	exit;
}

header('HTTP/1.0 404 Not Found');
print 'Not Found';
print " $file";
