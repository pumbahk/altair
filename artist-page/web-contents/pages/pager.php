<script language="php">
# こんな感じで
#	$unit = 10;
#	$pager = build_pager(array(
#		'unit' => $unit,	# １ページあたり最大表示件数
#		'self' => preg_replace('{([^/]*/)*}', '', $base),
#		'query' => $param_saved,	# リンク先に引き継ぐパラメータ(str or hash)
#		'qname' => 'p',	# ページ番号指定用のkey
#		'item' => $a,	# データ配列
#		'limit' => 10,	# ナビに表示するページ数上限
#	));
#	$data['pager'] = $pager['navi'];
#	$data['item'] = array_splice($a, ($pager['page']-1)*$unit, $unit);

function build_pager($param) {
	$fname = $param['self'] ? $param['self'] : preg_replace('{^/([^/]*/)*([^/\?]*)(\?.+)?$}', '$2', $_SERVER['REQUEST_URI']);
	$pu = $param['unit'] ? $param['unit'] :	10;
	$qname = $param['qname'] ? $param['qname'] : 'page';
	$a = $param['item'];
	$query = $param['query'];
	if(!is_array($query)) {
		parse_str($query, $query);
	}
	$pt = count($a);				# 総page数
	$px = floor(($pt+$pu-1)/$pu);	# 最終page
	$pc = !empty($query[$qname]) ? 1*$query[$qname] : 0;
	$pc = (1<=$pc && $pc<=$px) ? $pc : 1;	# 現在page
	$pp = (1<$pc) ? $pc-1 : "";		# 前ページ
	$pn = ($pc<$px) ? $pc+1 : "";	# 次ページ
	
	# n0は1か3以上 / nxはpxかpx-2以下
	if(!empty($param['limit'])) {
		$limit = $param['limit'];
		$n0 = max(1, min($px-$limit+1, ($pc-$limit/2 <= 1) ? 1 : ($pc-$limit/2 + 1)));
		$nx = min($px, $n0+$limit-1-(3 <= $n0?1:0)+($px <= $pc+$limit/2?1:0));
	} else {
		$n0 = 1;
		$nx = $px;
	}
	
	$pages = array();
	if(1 < $n0) {
		$pages[] = array('n' => 1, 'current' => (1==$pc)?1:0);
		$pages[] = array('text' => '...');
	}
	for($i=$n0 ; $i<=$nx ; $i++) {
		$pages[] = array('n' => $i, 'current' => ($i==$pc)?1:0);
	}
	if($nx < $px) {
		$pages[] = array('text' => '...');
		$pages[] = array('n' => $px, 'current' => ($px==$pc)?1:0);
	}
	
	unset($query[$qname]);
	$qstring = http_build_query($query);
	$result = array();
	$result['page'] = $pc;
	$result['navi'] = array(array(
		'item_count_unit' => $pu,								# ページあたり表示件数(上限値)
		'item_count' => $pt,									# [xx件みつかりました]の総件数
		'item_count_from' => ($pc-1)*$pu+1,						# [xx件目からyy件目を表示中]のxx
		'item_count_to' => min($pc*$pu, $pt),					# [xx件目からyy件目を表示中]のyy
		'item_count_prev' => $pp ? $pu : '',					# [前のxx件]のxx値
		'item_count_next' => $pn ? min($pt-$pc*$pu, $pu) : '',	# [次のxx件]のxx値
		'prev_page' => $pp ? "$fname?$qstring&$qname=$pp" : '',	# 前のページへのリンク
		'next_page' => $pn ? "$fname?$qstring&$qname=$pn" : '',	# 次のページへのリンク
		'goto_page' => "$fname?$qstring&$qname=",				# 指定ページへのリンク
		'navi_prev' => (1 < $n0) ? 1 : 0,						# navi前省略あり/なし
		'navi_next' => ($nx < $px) ? 1 : 0,						# navi後省略あり/なし
		'page_count' => $px,									# 総ページ数=最終ページ番号
		'pages' => $pages,
	));
	
	return $result;
}
</script>
