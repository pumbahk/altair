<%doc>
${queries}
detail search result
</%doc>

<%namespace file="../components.mako" name="co"/>

<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja"><!-- InstanceBegin template="/Templates/template.dwt" codeOutsideHTMLIsLocked="false" -->
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<!-- InstanceBeginEditable name="doctitle" -->
<title>チケット販売・イベントの予約 [音楽 / コンサート / 舞台 / スポーツ] - 楽天チケット</title>
<!-- InstanceEndEditable -->
<meta name="description" content="チケットの販売、イベントの予約は楽天チケットで！楽天チケットは演劇、バレエ、ミュージカルなどの舞台、クラシック、オペラ、ロックなどのコンサート、野球、サッカー、格闘技などのスポーツ、その他イベントなどのチケットのオンラインショッピングサイトです。" />
<meta name="keywords" content="チケット,演劇,クラシック,オペラ,コンサート,バレエ,ミュージカル,野球,サッカー,格闘技" />
<meta http-equiv="content-style-type" content="text/css" />
<meta http-equiv="content-script-type" content="text/javascript" />
<link rel="shortcut icon" href="/static/ticketstar/img/common/favicon.ico" />
<link rel="stylesheet" href="/static/ticketstar/css/import.css" type="text/css" media="all" />
<script type="text/javascript" src="/static/ticketstar/js/jquery.js"></script>
<!-- InstanceParam name="id" type="text" value="search" -->
</head>
<body id="search">

<p id="naviSkip"><a href="#main" tabindex="1" title="本文へジャンプ"><img src="/static/ticketstar/img/common/skip.gif" alt="本文へジャンプ" width="1" height="1" /></a></p>

<div id="container">

	<!-- ========== header ========== -->
	<div id="grpheader">
  	  ${co.master_header(top_outer_categories)}
    </div>
    ${co.global_navigation(top_inner_categories, categories)}
    ${co.header_search()}
	<!-- ========== /header ========== -->
	
	<hr />
	
	<!-- InstanceBeginEditable name="cat" --><h1><img src="/static/ticketstar/img/search/title_search.gif" alt="検索結果" width="118" height="60" /></h1>
<!-- InstanceEndEditable -->
	
	<!-- ========== main ========== -->
	<div id="main">
		<!-- InstanceBeginEditable name="main" -->
		<%block name="main"/>
		<!-- InstanceEndEditable -->
	</div>
	<!-- ========== /main ========== -->
	
	<hr />
	
	<!-- ========== side ========== -->
	<div id="side">
		<!-- InstanceBeginEditable name="side" -->
		<div class="sideCategoryGenre">
		<h2>カテゴリー一覧</h2>
		<ul>
			<li><a href="#">音楽</a></li>
			<li><a href="#">演劇</a></li>
			<li><a href="#">スポーツ</a></li>
			<li><a href="#">イベント・その他</a></li>
		</ul>
		</div>
		<div class="sideCategoryGenre">
		<h2>ジャンル一覧</h2>
		<ul>
			<li><a href="#">J-POP・ROCK</a></li>
			<li><a href="#">海外ROCK・POPS</a></li>
			<li><a href="#">フェスティバル</a></li>
			<li><a href="#">ジャズ・フュージョン</a></li>
			<li><a href="#">アニメ音楽</a></li>
			<li><a href="#">演歌・邦楽</a></li>
			<li><a href="#">童謡・日本のうた</a></li>
			<li><a href="#">民族音楽</a></li>
			<li><a href="#">シャンソン</a></li>
			<li><a href="#">音楽その他</a></li>
		</ul>
		</div>
		<dl id="sideRefineSearch">
			<dt>エリアを選択</dt>
			<dd>
				<ul>
					<li><a href="#">北海道</a></li>
					<li><a href="#">東北</a></li>
					<li><a href="#">関東甲信越</a></li>
					<li><a href="#">中部</a></li>
					<li><a href="#">北陸</a></li>
					<li><a href="#">関西</a></li>
					<li><a href="#">中国・四国</a></li>
					<li><a href="#">九州・沖縄</a></li>
				</ul>
			</dd>
			<dt>販売状態で絞込み</dt>
			<dd>
				<ul>
					<li><a href="#">最速抽選</a></li>
					<li><a href="#">先行抽選</a></li>
					<li><a href="#">先行先着</a></li>
					<li><a href="#">一般発売</a></li>
					<li><a href="#">追加抽選</a></li>
				</ul>
			</dd>
			<dt>発売日・受付日で絞込み</dt>
			<dd>
				<ul>
					<li><a href="#">7日以内に受付・発売開始</a></li>
					<li><a href="#">14日以内に受付・発売開始</a></li>
					<li><a href="#">30日以内に受付・発売開始</a></li>
				</ul>
			</dd>
			<dt>公演日で絞込み</dt>
			<dd>
				<ul>
					<li><a href="#">7日以内に公演</a></li>
					<li><a href="#">14日以内に公演</a></li>
					<li><a href="#">30日以内に公演</a></li>
				</ul>
			</dd>
		</dl>
		<dl id="sideInfo">
			<dt><img src="/static/ticketstar/img/common/side_info_title.gif" alt="お知らせ" width="190" height="18" /></dt>
			<dd>
				<ul>
					<li>2011年12月4日(日)　～　2011年12月4日(日)　メンテナンスを行います</li>
					<li>2011年12月4日(日)　～　2011年12月4日(日)　メンテナンスを行います</li>
				</ul>
			</dd>
		</dl>
		<!-- InstanceEndEditable -->
		<ul id="sideBtn">
			<li><a href="#"><img src="/static/ticketstar/img/mypage/btn_use.gif" alt="楽天チケットの使い方" width="202" height="28" /></a></li>
			<li><a href="#"><img src="/static/ticketstar/img/mypage/btn_favorite.gif" alt="お気に入りアーティストを登録" width="202" height="28" /></a></li>
			<li><a href="#"><img src="/static/ticketstar/img/mypage/btn_magazine.gif" alt="メルマガの購読" width="202" height="28" /></a></li>
		</ul>
	</div>
	<!-- ========== /side ========== -->
	
	<hr />
	
	<!-- ========== footer ========== -->
	${co.master_footer()}
	<!-- ========== /footer ========== -->

<!-- /container --></div>

</body>
<!-- InstanceEnd --></html>

