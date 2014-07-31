<?php

require 'site.php';
require 'db.php';

ini_set('include_path', 'lib:'.ini_get('include_path'));
require 'parser.php';

require 'common.php';

$id = sprintf('%u', $_GET['site']);

if(!$id) {
	print "Wrong param.";
	exit;
}

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

if(!empty($_POST['check'])) {
	header('Content-Type: text/plain');
	
	ini_set('display_errors', 1);
	print "Checking...\n";
	
	# バックエンド
	$url = get_s3_url($site['backend_metadata_url']);
	$json = json_decode(file_get_contents($url));
	foreach($json->pages as $k => $v) {
		$root = $k;
		break;
	}
	
	$dir = preg_replace('{/[^/]+$}', '', $site['backend_metadata_url']);
	$url = get_s3_url("$dir/$root");
	$xml = simplexml_load_file($url);
	$b_ids = get_object_ids($xml);
	print "founds ".count($b_ids)." seats in backend.\n";
	
	# フロント
	if(!empty($_POST['frontend'])) {
		$frontend = preg_replace('{^[^#]+#/venue-admin/}', '../', $_POST['frontend']);
	} else {
		# 登録済みのを使う
		$frontend = $site['_metadata_path'];
	}
	$path = preg_replace('{/[^/]+$}', '', $site['metadata_url']);
	$url = get_s3_url("$path/metadata.json");
	$decoded = json_decode(file_get_contents($url));
	$files = array_keys((array) $decoded->pages);
	
	$covered = 0;
	foreach($files as $f) {
		$fp = gzopen(get_s3_url("$path/$f"), 'r');
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
	exit;
}

/*
if(!empty($_POST['replace'])) {
	if(!preg_match('/^[a-z][a-z0-9-]+$/', $_POST['dir'])) {
		print "wrong dir name.\n";
		exit;
	}
	header('Content-Type: text/plain');
	$frontend = preg_replace('{^[^#]+#/venue-admin/}', '', $_POST['frontend']);
	system("BASENAME=".$_POST['dir']." SITE_ID=".$site['id']." FRONTEND=".$frontend." /home/taku/script/regc.sh 2>&1");
	
	exit;
}
*/

$parser = new Parser;

$svgs = array();
if(file_exists($site['_metadata_path'])) {
	$json = json_decode(file_get_contents($site['_metadata_path']));
	foreach($json->pages as $filename => $file) {
		$svgs[] = array('filename' => $filename, 'name' => $file->name);
	}
}

$r = $dbh->prepare("SELECT count(*) count FROM Seat s,Venue v WHERE site_id=? AND s.venue_id=v.id and v.performance_id IS NULL");
$r->execute(array($id));
$t = $r->fetch(PDO::FETCH_ASSOC);
$count = $t['count'];

$r = $dbh->prepare("SELECT v.id, p.event_id event, p.id performance, p.name performance_name, p.start_on, v.created_at,COUNT(s.id) count FROM Venue v LEFT JOIN Performance p ON p.id=v.performance_id LEFT JOIN Seat s ON s.venue_id=v.id WHERE site_id=? AND p.deleted_at IS NULL AND v.deleted_at IS NULL GROUP BY v.id");
$r->execute(array($id));
while($t = $r->fetch(PDO::FETCH_ASSOC)) {
	$venue[] = $t;
}

$r = $dbh->prepare("SELECT host_name FROM Host h, Site s,Venue v WHERE s.id=? and h.organization_id=v.organization_id and v.site_id=s.id and v.performance_id is null ORDER BY IF(host_name LIKE '%tstar.jp', 0, 1), IF(host_name LIKE '%.stg%', 1, 0)");
$t = $r->execute(array($id));

$data = array(
      'host' => $t['host_name'],
      'dir' => dirname($site['metadata_url']),
      'site' => array($site),
      'count' => $count,
      'venue' => $venue,
      'svgs' => $svgs,
);
$parser->parse(file_get_contents('template/site.html'), $data);
