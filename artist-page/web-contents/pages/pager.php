<script language="php">
# ����ʴ�����
#	$unit = 10;
#	$pager = build_pager(array(
#		'unit' => $unit,	# ���ڡ������������ɽ�����
#		'self' => preg_replace('{([^/]*/)*}', '', $base),
#		'query' => $param_saved,	# �����˰����Ѥ��ѥ�᡼��(str or hash)
#		'qname' => 'p',	# �ڡ����ֹ�����Ѥ�key
#		'item' => $a,	# �ǡ�������
#		'limit' => 10,	# �ʥӤ�ɽ������ڡ��������
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
	$pt = count($a);				# ��page��
	$px = floor(($pt+$pu-1)/$pu);	# �ǽ�page
	$pc = !empty($query[$qname]) ? 1*$query[$qname] : 0;
	$pc = (1<=$pc && $pc<=$px) ? $pc : 1;	# ����page
	$pp = (1<$pc) ? $pc-1 : "";		# ���ڡ���
	$pn = ($pc<$px) ? $pc+1 : "";	# ���ڡ���
	
	# n0��1��3�ʾ� / nx��px��px-2�ʲ�
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
		'item_count_unit' => $pu,								# �ڡ���������ɽ�����(�����)
		'item_count' => $pt,									# [xx��ߤĤ���ޤ���]������
		'item_count_from' => ($pc-1)*$pu+1,						# [xx���ܤ���yy���ܤ�ɽ����]��xx
		'item_count_to' => min($pc*$pu, $pt),					# [xx���ܤ���yy���ܤ�ɽ����]��yy
		'item_count_prev' => $pp ? $pu : '',					# [����xx��]��xx��
		'item_count_next' => $pn ? min($pt-$pc*$pu, $pu) : '',	# [����xx��]��xx��
		'prev_page' => $pp ? "$fname?$qstring&$qname=$pp" : '',	# ���Υڡ����ؤΥ��
		'next_page' => $pn ? "$fname?$qstring&$qname=$pn" : '',	# ���Υڡ����ؤΥ��
		'goto_page' => "$fname?$qstring&$qname=",				# ����ڡ����ؤΥ��
		'navi_prev' => (1 < $n0) ? 1 : 0,						# navi����ά����/�ʤ�
		'navi_next' => ($nx < $px) ? 1 : 0,						# navi���ά����/�ʤ�
		'page_count' => $px,									# ��ڡ�����=�ǽ��ڡ����ֹ�
		'pages' => $pages,
	));
	
	return $result;
}
</script>
