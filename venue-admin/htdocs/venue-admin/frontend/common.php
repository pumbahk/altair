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
