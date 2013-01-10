<pre>
<?php
include 'db.php';

include 'pager.php';

	$a = array();
	for($i=0;$i<52;$i++){
	
	 $a[]=array ('name'=>'kato'.($i+1));
	
	}
	$unit = 30;
	$pager = build_pager(array(
		'unit' => $unit,	# １ページあたり最大表示件数
#		'self' => preg_replace('{([^/]*/)*}', '', $base),
#		'query' => $param_saved,	# リンク先に引き継ぐパラメータ(str or hash)
		'query' => $_GET,
		'qname' => 'p',	# ページ番号指定用のkey
		'item' => $a,	# データ配列
		'limit' => 10,	# ナビに表示するページ数上限
	));
#print_r($pager);

?></pre>

<?php
foreach($pager['navi'][0]['pages'] as $p) {
	if($p['current']) {
		printf(' <b>%s</b>', $p['n']);
	} else {
		printf(' %s <a href="%s">%s</a>', $p['text'], $pager['navi'][0]['goto_page'].$p['n'], $p['n']);
	}
}
?>
<pre>
<?php
print_r(array_splice($a, ($pager['page']-1)*$unit, $unit));
