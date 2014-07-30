<?php

function get_object_ids($xml) {
	$ids = array();
	$xml->registerXPathNamespace('svg', 'http://www.w3.org/2000/svg');
	foreach($xml->xpath('//svg:metadata') as $m) {
		$m->registerXPathNamespace('si', 'http://xmlns.ticketstar.jp/2012/site-info');
		$object_list = $m->xpath('si:object');
		$class_name = array_shift($object_list[0]->xpath('si:class'));
		if($class_name == 'Seat') {
			$parent_id = (string) array_shift($m->xpath('parent::*/@id'));
			$attrs = $object_list[0]->attributes();
			if($attrs['prototype']) {
				#print "id: ".$parent_id."\n";
				#print "prototype: ".$attrs['prototype']."\n";
				if(isset($ids[$parent_id])) {
					print "WARN: dup ".$parent_id."\n";
				}
				$seat = array_shift($object_list[0]->xpath('si:property'));
				$ids[$parent_id] = array(
					'seat_name' => (string) $seat,
				);
			}
		}
	}
	return $ids;
}

function get_object_ids_frontend($xml) {
	$ids = array();
	$xml->registerXPathNamespace('svg', 'http://www.w3.org/2000/svg');
	foreach($xml->xpath('//svg:*') as $m) {
		$tagname = $m->getName();
		if(in_array($tagname, array('svg', 'title', 'text'))) {
			continue;
		}
		$id = (string) $m->attributes()->id;
		if($id) {
			$ids[$id] = $m;
		}
	}
	return $ids;
}

if(isset($argv[1])) {
	$backend = BACKEND_STORAGE.'/'.'venue-layouts/svgs/'.$argv[1].'.xml';
	$frontend = FRONTEND_STORAGE.'/'.'venue-layouts/frontend/'.$argv[1].'/metadata.json';
	
	print "backend: $backend\n";
	print "frontend: $frontend\n";
}

require_once 'site.php';

if(!is_file($backend)) {
	print "$backend missing.\n";
	exit(0);
}

if(!is_file($frontend)) {
	print "$frontend missing.\n";
	exit(0);
}

$b_ids = array();
$xml = simplexml_load_file($backend);

$b_ids = get_object_ids($xml);

print "founds ".count($b_ids)." seats in backend.\n";

$decoded = json_decode(file_get_contents($frontend));
$files = array_keys((array) $decoded->pages);

$covered = 0;
foreach($files as $f) {
	$fp = gzopen(dirname($frontend).'/'.$f, 'r');
	if(!$fp) {
		 print "failed";
		 exit;
	}
	$buf = "";
	while(!gzeof($fp)) {
		$buf .= gzread($fp, 16636);
	}
	$xml = simplexml_load_string($buf);
	
	$f_ids = get_object_ids_frontend($xml);
	print "founds ".count($f_ids)." ids in frontend: $f\n";
	foreach($f_ids as $id => $type) {
		if(isset($b_ids[$id])) {
			# OK
			if($b_ids[$id] !== true) {
				$b_ids[$id] = true;
				$covered++;
			} else {
				# 2度目
			}
		} else {
			# フロントにあるのにバックエンドに無い
			$tagname = $type->getName();
		#	print "no $id in backend ($tagname).\n";
		#	$b_ids[$id] = true;	 # 2度警告しないように
		}
	}
}

# 統計的な数字を
if(isset($argv[1])) {
	print $argv[1]."\t";
}
printf("Coverage: %.2f%% (%u/%u)\n", $covered/count($b_ids)*100, $covered, count($b_ids));
if($covered < count($b_ids)) {
	printf("Following %s seats are not selecable in frontend venue.\n", count($b_ids) - $covered);
	foreach($b_ids as $id => $obj) {
		if($obj !== true) {
			# バックエンドにあるが、フロントにない
			print "  $id ".$obj['seat_name']."\n";
		}
	}
}
