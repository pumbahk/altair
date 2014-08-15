<?php

require_once 'config.php';
require_once 'common.php';
require_once 'db.php';

header("Content-Type: text/html; charset=UTF-8");

if(@$_GET['env']) { print_r($_SERVER); exit; }

if(!empty($_POST['backend'])) {
	$backend = BACKEND_STORAGE.'/'.basename($_POST['backend']);
}
if(!empty($_POST['frontend'])) {
	$frontend = FRONTEND_STORAGE.'/'.preg_replace('/^.+\/([^\/]+\/[^\/]+?)(\.raw)?\.json$/', '$1.json', $_POST['frontend']);
}

if(!empty($_POST['check'])) {
	if(empty($_POST['site'])) {
		if(empty($backend)) {
			print "backend is required.\n";
			exit(0);
		}
		if(!is_file($backend)) {
			print "$backend missing.\n";
			exit(0);
		}
		if(!is_file($frontend)) {
			print "$frontend missing.\n";
			exit(0);
		}
		print "<pre>";
		check($backend, $frontend);
	} else {
		$site = get_site($_POST['site']);
		if(empty($site['backend_metadata_url']) || !preg_match('/\.json$/', $site['backend_metadata_url'])) {
			print "no backend in this site.";
			exit;
		}
		$url = get_s3_url($site['backend_metadata_url']);
		$json = json_decode(file_get_contents($url));
		if(!$json) {
			print "cannot fetch metadata of backend or broken.";
			exit;
		}
		foreach($json->pages as $k => $v) {
			$root = $k;
			break;
		}
		
		$dir = preg_replace('{/[^/]+$}', '', $site['backend_metadata_url']);
		if(empty($frontend)) {
			print "frontend is required.";
			exit;
		}
		echo '<pre>';
		check(get_s3_url("$dir/$root"), $frontend);
	}
	exit;
}

if(!empty($_POST['register'])) {
	if(empty($backend)) {
		print "backend is required.\n";
		exit;
	}
	if(!empty($_POST['backend_dirname'])) {
		$backend_dirname = $_POST['backend_dirname'];
	} else {
		$backend_dirname = preg_replace('{^.+?([^\./]+)\.xml$}', '$1', $backend);
	}
	if(empty($frontend)) {
		$frontend = "''";
		$frontend_dirname = "''";
	} else {
		if(!empty($_POST['frontend_dirname'])) {
			$frontend_dirname = $_POST['frontend_dirname'];
		} else {
			$frontend_dirname = $backend_dirname;
		}
	}
	$org = empty($_POST['organization']) ? "''" : $_POST['organization'];
	$pref = empty($_POST['prefecture']) ? "''" : bin2hex($_POST['prefecture']);
	$sub_name = empty($_POST['sub_name']) ? "''" : bin2hex($_POST['sub_name']);
	
	print "<pre>";
	$cmd = CMD_START_IMPORT_VENUE." $backend $frontend $org $pref $sub_name $backend_dirname $frontend_dirname 2>&1";
	print $cmd."\n";
	system($cmd);
	exit;
}

if(!empty($_POST['replace'])) {
	$site = $_POST['site'];
	if(empty($site)) {
		exit;
	}
	if(empty($frontend)) {
		print "frontend is required.\n";
		exit;
	}
	if(empty($_POST['frontend_dirname'])) {
		print "frontend_dirname is required.\n";
		exit;
	}
	$dirname = $_POST['frontend_dirname'];
	
	print "<pre>";
	$cmd = CMD_REGISTER_FRONTEND." $site $frontend $dirname 2>&1";
	print $cmd."\n";
	system($cmd);
	exit;
}

?>
<div style="position: absolute; right: 10px; width: 300px; height: 200px;">
<iframe src="ps.php" style="width: 300px; height: 200px;"></iframe>
<br />(auto updated at 10 seconds interval)
</div>

<?php if(empty($_GET['site'])) { ?>
<form method="post" target="output">
backend: <input type="text" name="backend" value="" style="width: 500px;" placeholder="http://hostname/chk.html#/upload/backend/ffffffffffff.gotanda-hall.xml" />
<br />
frontend: <input type="text" name="frontend" value="" style="width: 500px;" placeholder="http://hostname/vwr.html#/upload/frontend/ffffffffffff/metadata.json" /> (optional)
<br /> 
organization: <select name="organization">
<option name=""></option>
<?php
foreach(explode("\n", shell_exec(CMD_LIST_ORGS)) as $o_op) {
	if($o_op) {
		list($o, $op) = explode("\t", rtrim($o_op));
		printf('<option value="%s">%s%s</option>', htmlspecialchars($o), htmlspecialchars($o), $op!="NULL"?" (".htmlspecialchars($op)."他)":"");
	}
}
?>
</select>
<br />
sub_name: <input type="text" name="sub_name" />
<br />
prefecture: <input type="text" name="prefecture" />
<br />
backend-dirname: <input type="text" name="backend_dirname" /> (通常は空欄で構いません)
<br />
frontend-dirname: <input type="text" name="frontend_dirname" /> (通常は空欄で構いません)
<br />
<input type="submit" name="register" value="backend(+frontend)を新規登録する" />
<br />
<input type="submit" name="check" value="整合性チェックする" />
</form>
<?php } else { ?>
    <?php
    $r = $dbh->prepare('SELECT * FROM Site WHERE id=?');
    $r->execute(array($_GET['site']));
    $site = $r->fetch(PDO::FETCH_ASSOC);
    if(!$site) {
    	print "no such site.";
    	exit;
    }
    $dirname = basename(dirname($site['metadata_url']));
    ?>
<form method="post" target="output">
site: <input type="hidden" name="site" value="<?php echo $site['id']; ?>" />
<?php echo $site['id']; ?>
<?php echo $site['name']; ?>
<br />
frontend: <input type="text" name="frontend" value="" style="width: 500px;" placeholder="http://hostname/vwr.html#/upload/frontend/ffffffffffff/metadata.json" />
<br /> 
frontend-dirname: <input type="text" name="frontend_dirname" value="<?php echo $dirname; ?>" /> (差し替えの際は変更を推奨)
<br />
<input type="submit" name="replace" value="frontendを追加登録/差し替える (ちょっと時間がかかります)" />
<br />
<input type="submit" name="check" value="整合性チェックする" />
</form>
<br />
<br />
<?php } ?>
<div style="height: 100px;"></div>

<iframe name="output" style="width: 100%;" src="./"></iframe>
