<?php

include 'aws.phar';

use Aws\S3\S3Signature;
use Aws\Common\Credentials\Credentials;

function get_s3_url($url) {
	$timestamp = time() + 300;
	if(preg_match('{^s3://([^/]+)(/.*)$}', $url, $m)) {
		$bucket_name = $m[1];
		$path = $m[2];
	} else {
		return false;
	}
	$s3s = new S3Signature();
	$sign = $s3s->signString("GET\n\n\n"
		."$timestamp\n"
		."/$bucket_name$path",
		new Credentials(AWS_KEY, AWS_SECRET, null, $timestamp)
	);
	return sprintf('https://%s.s3.amazonaws.com%s?Signature=%s&Expires=%u&AWSAccessKeyId=%s',
	       $bucket_name, $path, urlencode($sign), $timestamp, AWS_KEY);
}

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

function check($backend_xml_path, $frontend_json_path) {
	$xml = simplexml_load_file($backend_xml_path);
	$b_ids = get_object_ids($xml);
	print "founds ".count($b_ids)." seats in backend.\n";

	$decoded = json_decode(file_get_contents($frontend_json_path));
	$files = array_keys((array) $decoded->pages);
	
	$covered = 0;
	foreach($files as $f) {
		$fp = gzopen(dirname($frontend_json_path).'/'.$f, 'r');
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
}

function get_site($id) {
	global $dbh;
	$r = $dbh->prepare("SELECT s.*, v.sub_name FROM Site s LEFT JOIN Venue v ON v.site_id=s.id WHERE s.id=?");
	$r->execute(array($id));
	$site = $r->fetch(PDO::FETCH_ASSOC);
	$site['_metadata_path'] = "../../../var/venue-layouts/frontend/".$site['metadata_url'];
	
	if(strpos($site['backend_metadata_url'], ':') == FALSE) {
		$site['backend_metadata_url'] = 's3://tstar/venue-layouts/backend/'.$site['backend_metadata_url'];
	}
	$site['dirname'] = basename(dirname($site['backend_metadata_url']));
	if(!empty($site['metadata_url']) && strpos($site['metadata_url'], ':') == FALSE) {
		$site['metadata_url'] = 's3://tstar/venue-layouts/frontend/'.$site['metadata_url'];
	}
	return $site;
}
