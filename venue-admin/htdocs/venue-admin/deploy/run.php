<?php

require_once 'site.php';

header("Content-Type: text/html; charset=UTF-8");

if(!empty($_POST['backend'])) {
	$backend = BACKEND_STORAGE.'/'.basename($_POST['backend']);
}
if(!empty($_POST['frontend'])) {
	$frontend = FRONTEND_STORAGE.'/'.preg_replace('/^.+\/([^\/]+\/[^\/]+)(\.raw)?\.json$/', '$1.json', $_POST['frontend']);
}

if(!empty($_POST['check'])) {
	echo '<pre>';
	include 'check.php';
	exit;
}

require_once 'site.php';

if(!empty($_POST['register'])) {
	if(empty($backend)) {
		print "backend is required.\n";
		exit;
	}
	if(!empty($_POST['filename'])) {
		$dirname = $_POST['filename'];
	} else {
		$dirname = preg_replace('{^.+?([^\./]+)\.xml$}', '$1', $backend);
	}
	if(empty($frontend)) { $frontend = "''"; }
	$org = empty($_POST['organization']) ? "''" : $_POST['organization'];
	$pref = empty($_POST['prefecture']) ? "''" : bin2hex($_POST['prefecture']);
	$sub_name = empty($_POST['sub_name']) ? "''" : bin2hex($_POST['sub_name']);
	
	print "<pre>";
	$cmd = CMD_START_IMPORT_VENUE." $dirname $backend $frontend $org $pref $sub_name 2>&1";
	print $cmd."\n";
	system($cmd);
	exit;
}

if(!empty($_POST['replace'])) {
	if(empty($_POST['filename'])) {
		print "filename is required.\n";
		exit;
	}
	$dirname = $_POST['filename'];
	$backend = "''";
	if(empty($frontend)) {
		print "frontend is required.\n";
		exit;
	}
	
	print "<pre>";
	$cmd = CMD_IMPORT_VENUE." $dirname $backend $frontend 2>&1";
	print $cmd."\n";
	system($cmd);
	exit;
}

?>
<div style="position: absolute; right: 10px; width: 300px; height: 200px;">
<iframe src="ps.php" style="width: 300px; height: 200px;"></iframe>
<br />(auto updated at 10min interval)
</div>

<form method="post" target="output">
backend: <input type="text" name="backend" value="" style="width: 500px;" placeholder="http://hostname/chk.html#/upload/backend/ffffffffffff.gotanda-hall.xml" />
</select>
<br />
frontend: <input type="text" name="frontend" value="" style="width: 500px;" placeholder="http://hostname/vwr.html#/upload/frontend/ffffffffffff/metadata.json" />
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
filename: <input type="text" name="filename" value="<?php echo htmlspecialchars(@$_GET['filename']); ?>" /> (新規登録時は空欄で構いません)
<br />
<input type="submit" name="register" value="backend(+frontend)を新規登録する" />
<br />
<input type="submit" name="replace" value="frontendを追加登録/差し替える" />
<br />
<input type="submit" name="check" value="整合性チェックする" />
</form>

<div style="height: 100px;"></div>

<iframe name="output" style="width: 100%;" src="./"></iframe>
