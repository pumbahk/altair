<?php

require_once 'site.php';

function pack_svg($src, $dst) {
	$pp = popen("xsltproc strip-metadata.xsl $src | gzip", 'r');
	if(!$pp) {
		print "xsltproc or gzip failed.";
		exit;
	}
	$fp = fopen($dst, 'w');
	while(!feof($pp)) {
		fwrite($fp, fread($pp, 1024*1024));
	}
	fclose($pp);
	fclose($fp);
}

function build_metadata($name) {
	return sprintf('{
    "pages": {
        "%s": {
            "name": "全体図",
            "root": true
        }
    }
}
', $name);
}

function get_frontend_venue_name($file) {
	if(preg_match('/\.svgz$/', $file)) {
		$xml = simplexml_load_string(join('', gzfile($file)));
	} else {
		$xml = simplexml_load_file($file);
	}
	foreach($xml->xpath('//si:object') as $o) {
		foreach($o->xpath('//si:class') as $c) {
			if((string) $c == 'Venue') {
				foreach($c->xpath('//si:property') as $p) {
					if($p['name'] == 'name') {
						return (string) $p;
					}
				}
			}
		}
	}
}

if(@$_FILES['back'] && @$_FILES['back']['tmp_name']) {
	$xml = simplexml_load_file($_FILES['back']['tmp_name']);
	
	$count = 0;
	foreach($xml->xpath('//si:object/si:class') as $c) {
		if(((string) $c[0]) == 'Seat') {
			$count++;
		}
	}
	
	$meta = array(
		'name' => (string) $xml->title,
		'seat_count' => $count,
		'uploaded_by' => @$_SERVER['PHP_AUTH_USER'],
	);

	$name = uniqid();
	if(preg_match('/^([a-z0-9-\.]+)\.xml$/i', $_FILES['back']['name'], $matches)) {
		$name .= ".".$matches[1];
	}

	file_put_contents(BACKEND_STORAGE."/$name.xml.meta", json_encode($meta));
	
	copy($_FILES['back']['tmp_name'], BACKEND_STORAGE."/$name.xml");
	
	$url = sprintf('%s://%s%s/checker.html#%s', empty($_SERVER['HTTPS']) ? 'http' : 'https',
		$_SERVER['HTTP_HOST'], dirname($_SERVER['SCRIPT_NAME']),
		dirname($_SERVER['SCRIPT_NAME']).'/backend/'.$name.'.xml');
	
	header("Location: $url");
	exit;
}

if(@$_FILES['front']) {
	$name = uniqid();
	mkdir(FRONTEND_STORAGE."/$name");
	chmod(FRONTEND_STORAGE."/$name", 0777);
	
	$json = null;
	$files = array();
	for($i=0 ; $i < count($_FILES['front']['name']) ; $i++) {
		$filename = $_FILES['front']['name'][$i];
		if(preg_match('/\.\./', $filename) || preg_match('{(/|\\|\s|%)}', $filename)) {
			# dangerous filename !
			continue;
		}	
		if(preg_match('/\.json$/i', $filename)) {
			$content = file_get_contents($_FILES['front']['tmp_name'][$i]);
			$content = preg_replace('/^\xef\xbb\xbf/', '', $content);	// remove BOM
			# for plain version
			file_put_contents(FRONTEND_STORAGE."/$name/metadata.raw.json", $content);
			
			# for gzipped version
			$dst = new stdClass();
			foreach(json_decode($content) as $key => $data) {
				if($key == 'pages') {
					$pages = new stdClass();
					foreach($data as $svgname => $svgmeta) {
						$svgname = preg_replace('/\.svg$/', '.svgz', $svgname);
						$pages->$svgname = $svgmeta;
					}
					$dst->$key = $pages;
				} else {
					$dst->$key = $data;
				}
			}
			file_put_contents($json=FRONTEND_STORAGE."/$name/metadata.json", json_encode($dst));
		} elseif(preg_match('/\.svg$/i', $filename)) {
			$files[] = FRONTEND_STORAGE."/$name/$filename";		# .svg
			copy($_FILES['front']['tmp_name'][$i], FRONTEND_STORAGE."/$name/$filename");
			
			pack_svg($_FILES['front']['tmp_name'][$i], FRONTEND_STORAGE."/$name/$filename"."z");
		}
		chmod(FRONTEND_STORAGE."/$name/".$filename, 0666);
	}
	
	if(count($files) == 0) {
		print "require .svg file.";
		exit;
	}
	
	if(!$json) {
		file_put_contents(FRONTEND_STORAGE."/$name/metadata.raw.json", build_metadata(basename($files[0])));
		
		file_put_contents($json=FRONTEND_STORAGE."/$name/metadata.json", build_metadata(preg_replace('/\.svg$/', '.svgz', basename($files[0]))));
	}
	
	file_put_contents($json.".meta", json_encode(array(
		'name' => get_frontend_venue_name($files[0]),
		'uploaded_by' => @$_SERVER['PHP_AUTH_USER'],
	)));
	chmod($json.".meta", 0666);
	
	$url = sprintf('%s://%s%s/viewer.html#%s', empty($_SERVER['HTTPS']) ? 'http' : 'https',
		$_SERVER['HTTP_HOST'], dirname($_SERVER['SCRIPT_NAME']),
		dirname($_SERVER['SCRIPT_NAME'])."/frontend/$name/metadata.json");
	
	header("Location: $url");
	
	exit;
}

header("Content-Type: text/html; charset=UTF-8");

?>
<script src="js/jquery-1.7.2.js"></script>
<script src="https://service.ticketstar.jp/static/js/jquery.chosen.js"></script>
<link rel="stylesheet" type="text/css" href="https://service.ticketstar.jp/static/css/chosen.css" />
<script>
$(function() {
	$('select').chosen();
});
</script>

<h1>venue uploader</h1>

<form method="post" enctype="multipart/form-data">
backend(.xml): <input type="file" name="back" />
<input type="submit" value="アップロード" />
</form>

<form onsubmit="location.href = 'checker.html#'+this.s.options[this.s.selectedIndex].value; return false;">
<select name="s" onchange="this.form.onsubmit();">
<option value=""></option>
<?php
$options = array();
$sorter = array();
$dh = opendir(BACKEND_STORAGE);
if(!$dh) {
	user_error("cannot open ".BACKEND_STORAGE, E_USER_ERROR);
}
while($f = readdir($dh)) {
	if(preg_match('/^(.+)\.meta$/', $f, $matches) && file_exists(BACKEND_STORAGE.'/'.$matches[1])) {
		$meta = json_decode(file_get_contents(BACKEND_STORAGE.'/'.$f));
		$mtime = filemtime(BACKEND_STORAGE.'/'.$f);
		$comment = sprintf('%s %s (%u席, %uKB) %s',
			date('Y-m-d H:i', $mtime),
			$meta->name, $meta->seat_count, filesize(BACKEND_STORAGE.'/'.$matches[1])/1024, $meta->uploaded_by ? 'by '.$meta->uploaded_by : '');
		$options[] = sprintf('<option value="%s">%s</option>'."\n",
			   dirname($_SERVER['SCRIPT_NAME']).'/backend/'.$matches[1], $comment);
		$sorter[] = $mtime;
	}
}
closedir($dh);
array_multisort($sorter, SORT_DESC, $options);
print join('', $options);
?>
</select>
<input type="submit" value="Go" />
</form>

<hr />
<form method="post" enctype="multipart/form-data">
frontend(.svg files and .json): <input type="file" name="front[]" multiple="multiple" />
<input type="submit" value="アップロード" />
<br />
(原則.jsonを1つ含めてアップロードしてください. ファイル名のベース部はmetadataじゃなくてもいいです. ただし.svgが1つの時は.svgだけでも大丈夫です. サーバ側で自動生成します.)
</form>

<form onsubmit="location.href = 'viewer.html#'+this.s.options[this.s.selectedIndex].value; return false;">
<select name="s" onchange="this.form.onsubmit();">
<option value=""></option>
<?php
$options = array();
$sorter = array();
$dh = opendir(FRONTEND_STORAGE);
while($d = readdir($dh)) {
	if(!is_dir(FRONTEND_STORAGE.'/'.$d)) {
		continue;
	}
	$ddh = opendir(FRONTEND_STORAGE.'/'.$d);
	while($f = readdir($ddh)) {
		if(preg_match('/^(.+)\.meta$/', $f, $matches) && file_exists(FRONTEND_STORAGE.'/'.$d.'/'.$matches[1])) {
			$meta = json_decode(file_get_contents(FRONTEND_STORAGE."/$d/$f"));
			$mtime = filemtime(FRONTEND_STORAGE."/$d/$f");
			$comment = sprintf('%s %s %s',
				date('Y-m-d H:i', $mtime),
				$meta->name,
				$meta->uploaded_by ? 'by '.$meta->uploaded_by : '');
			$options[] = sprintf('<option value="%s">%s</option>'."\n", dirname($_SERVER['SCRIPT_NAME']).'/frontend/'.$d.'/'.$matches[1], $comment);
			$sorter[] = $mtime;
		}
	}
	closedir($ddh);
}
closedir($dh);
array_multisort($sorter, SORT_DESC, $options);
print join('', $options);
?>
</select>
<input type="submit" value="Go" />
</form>

<hr />
<?php
printf('post_max_size=%s <br />', ini_get('post_max_size'));
printf('upload_max_filesize=%s <br />', ini_get('upload_max_filesize'));
?>
<!--
事前に<a href="http://c.stg2.rt.ticketstar.jp/">http://c.stg2.rt.ticketstar.jp/</a>の認証を通過しておいてください.
-->
