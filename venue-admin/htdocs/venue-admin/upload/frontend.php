<?php

require_once 'site.php';

$dir = ltrim(dirname($_SERVER['PATH_INFO']), '/');
$file = basename($_SERVER['PATH_INFO']);

if(preg_match('/\.\./', $dir)) {
	error();
}
if(substr($dir, 0, 1) == ".") {
	error();
}
if(!is_dir(FRONTEND_STORAGE."/$dir")) {
	error();
}
if(!is_file(FRONTEND_STORAGE."/$dir/$file")) {
	error();
}
$meta = json_decode(file_get_contents(FRONTEND_STORAGE."/$dir/$file"));
if(!$meta) {
	error();
}

if(@$_GET['name'] && $_GET['mode'] == 'seat_types') {
	$name = $_GET['name'];
	$parts = array();
	foreach($meta->pages as $filename => $meta) {
		$parts[$filename] = dirname($_SERVER['SCRIPT_NAME']).'/frontend/'.$dir.'/'.$filename;
	}

	$json = file_get_contents('template/seat_types.json.template');
	$json = str_replace(
	      array('${BASE}', '${DIR}', '${FILE}', '${VENUE}', '${PARTS}'),
	      array(dirname($_SERVER['SCRIPT_NAME']), $dir, $file, $name, json_encode($parts)),
	$json);
	header('Content-Type: text/javascript; charset=UTF=8');
	print json_encode(json_decode($json));
} else {
	$template = file_get_contents('template/seats.json.template');
	$json = str_replace('"pages": { }', '"pages": '.json_encode($meta->pages), $template);
	header('Content-Type: text/javascript; charset=UTF=8');
	print $json;
}


function error() {
	header('Content-Type: text/javascript; charset=UTF=8');
	print '{ }';
	exit;
}
