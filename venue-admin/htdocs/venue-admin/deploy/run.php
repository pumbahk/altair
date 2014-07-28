<?php

# print "Sorry, now maintenance by sasao\n";exit;

header("Content-Type: text/html; charset=UTF-8");

if(isset($_POST['backend'])) {
	$backend = basename($_POST['backend']);
}
if(isset($_POST['frontend'])) {
	$frontend = preg_replace('/^.+\/([^\/]+\/[^\/]+)(\.raw)?\.json$/', '$1.json', $_POST['frontend']);
}

if(!empty($_POST['check'])) {
	echo '<pre>';
	include 'check.php';
	exit;
}

require_once 'site.php';

if(!empty($_POST['register'])) {
	print "<pre>";
	if(empty($_POST['backend'])) { print "parameter error."; exit; }
	if($frontend == '') { $frontend = "''"; }
	$org = $_POST['organization'];
	$pref = empty($_POST['prefecture']) ? "''" : $_POST['prefecture'];
	$sub_name = empty($_POST['sub_name']) ? "''" : bin2hex($_POST['sub_name']);
	$filename = empty($_POST['filename']) ? "''" : $_POST['filename'];
	system(CMD_IMPORT_VENUE." $backend $frontend $org $pref $sub_name $filename 2>&1");
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
frontend: <input type="text" name="frontend" value="" style="width: 500px;" placeholder="http://hostname/vwr.html#/upload/frontend/ffffffffffff/metadata.json" /> (option)
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
filename: <input type="text" name="filename" /> (通常は空欄で構いません)
<br />
<input type="submit" name="register" value="本番環境に登録する" />
<br />
<input type="submit" name="check" value="整合性チェックする" />
</form>

<div style="height: 100px;"></div>

<iframe name="output" style="width: 100%;" src="./"></iframe>
