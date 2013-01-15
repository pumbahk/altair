<?php

include 'config.php';
include 'gojyuon_search.php';
include 'pager.php';
$result = gojyuon_search();
extract($result);
$unit = 30;
$base = '';
$pager = build_pager(array(
	'unit' => $unit,
	'self' => preg_replace('{([^/]*/)*}','',$base),
	'query' => $_GET,
	'qname' => 'p',
	'item' => $page_artist_array,
	'limit' => 10,
));
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transition//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja"><!- InstanceBegin templa
te="/Template/template.dwt" codeOutsideHTMLslocked="false" -->
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<!-- InstanceBeginEditable name="doctitle" --><title>検索ページ</title>
<!-- InstanceEndEditable -->
<meta name="description" content="チケットの販売、イベントの予約は楽天チケットで！楽天チケ>
ットは演劇、バレエ、ミュージカルなどの舞台、クラシック、オペラ、ロックなどのコンサート、野>
球、サッカー、格闘技などのスポーツ、その他イベントなどのチケットのオンラインショッピングサ>
イトです。" />
<meta name="keywords" content="チケット,演劇,クラシック,オペラ,コンサート,バレエ,ミュージカ
ル,野球,サッカー,格闘技" />
<meta http-equiv="content-style-type" content="text/css" />
<meta http-equiv="content-script-type" content="text/javascript" />
<link rel="shortcut icon" href="../design/img/common/favicon.ico" />
<link rel="stylesheet" href="../design/html/css/import.css" type="text/css" media="all" />
<link rel="stylesheet" href="./css/import.css" type="text/css" media="all" />
<script type="text/javascript" src="http://www.google.com/jsapi"></script>
<script type="text/javascript">google.load("jquery", "1.6.1");</script>
<script type="text/javascript" src="./js/gojyuon.js"></script>
<script type='text/javascript' src='js/tooltip.js'></script>
<link rel="stylesheet" href="./css/gojyuon.css" type="text/css" media="all" />
<script type ="text/javascript">
$(function() {
   $('#accordion dd').hide();
   $('#accordion dt a').click(function(){
       $('#accordion dd').slideUp();
       $(this).parent().next().slideDown();
       return false;
   });
});
</script>
<!-- InstanceParam name="id" type="text" value="theater" -->
</head>
<body id="theater" >
<p id="naviSkip"><a href="#main" tabindex="1" title="本文へジャンプ"><img src="../img/commo
n/skip.gif" alt="本文へジャンプ" width="1" height="1" /></a></p>
<div id="container">
	<!-- ========== header ========== -->
	<div id="grpheader">
	<!-- ========== header ========== -->
	<div id="grpheader">
		<p id="tagLine">チケット販売・イベント予約</p>
		<p id="siteID"><a href="http://ticket.rakuten.co.jp/"><img src="../img/common/header_logo_01.gif" alt="楽天チケット" class="serviceLogo" width="97" height="35" /></a><a href="http://ticket.rakuten.co.jp/"><img src="../img/common/header_logo_02.gif" alt="チ>ケット" class="serviceTitle" width="88" height="23" /></a></p>
		<dl id="remoteNav">
			<dt>楽天グループ関連</dt>
			<dd class="grpRelation">
				<ul><!--
				--><li id="grpNote"><noscript><a href="https://card.rakuten.co.jp/entry/">今すぐ2,000ポイント！</a></noscript></li><!--
				--><li><a href="#">必見！5,000ポイントがもらえる</a></li><!--
				--><li class="grpHome"><a href="http://www.rakuten.co.jp/">楽天市場へ</a></li><!--
				--></ul>
				<script type="text/javascript" src="//jp.rakuten-static.com/1/js/lib/prm_selector.js"></script>
				<script type="text/javascript" src="//jp.rakuten-static.com/1/js/grp/hdr/prm_sender.js"></script>
			</dd>
<dt>補助メニュー</dt>
			<dd class="siteUtility">
				<ul><!--
				--><li><a href="#">初めての方へ</a></li><!--
				--><li><a href="#">公演中止・変更情報</a></li><!--
				--><li><a href="#">ヘルプ</a></li><!--
				--><li class="last"><a href="#">サイトマップ</a></li><!--
				--></ul>
			</dd>
		</dl>
	</div>
	<div id="globalNav">
		<ul id="globalNav1">
			<li><a href="./index.php"><img src="../img/common/header_nav_top.gif" alt="チケットトップ" width="132" height="40" /></a></li>
			<li><a href="../music/index.html"><img src="../img/common/header_nav_music.gif" alt="音楽" width="67" height="40" /></a></li>
			<li><a href="index.html"><img src="../img/common/header_nav_theater.gif" alt="演劇" width="73" height="40" /></a></li>
			<li><a href="../sports/index.html"><img src="../img/common/header_nav_sports.gif" alt="スポーツ" width="102" height="40" /></a></li>
			<li><a href="../event/index.html"><img src="../img/common/header_nav_event.gif" alt="イベント・その他" width="157" height="40" /></a></li>
		</ul>
		<ul id="globalNav2">
			<li><a href="#">抽選申込履歴</a></li>
			<li><a href="#">購入履歴</a></li>
			<li><a href="#">お気に入り</a></li>
			<li><a href="#">マイページ</a></li>
		</ul>
	</div>
	<div id="headerSearch">
		<form id="form1" name="form1" method="post" action="">
			<input name="textfield" type="text" id="textfield" size="40" value="アーティスト名、公演名、会場名など" onblur="if(this.value=='') this.value='アーティスト名>、公演名、会場名など';" onfocus="if(this.value=='アーティスト名、公演名、会場名など') this.value='';" />
			<input name="imageField" type="image" id="imageField" src="../img/common/header_search_btn.gif" alt="検索" />
			<a href="#">詳細検索</a>
		</form>
		<dl>
			<dt><img src="../img/common/header_search_hot.gif" alt="ホットワー>ド" width="50" height="45" /></dt>
			<dd>
				<ul>
					<li><a href="#">サッカー</a></li>
					<li><a href="#">ブルーマン</a></li>
					<li><a href="#">きゃりーぱみゅぱみゅ</a></li>
					<li><a href="#">クーザ</a></li>
					<li><a href="#">オンタマ</a></li>
					<li><a href="#">ももいろクローバーZ</a></li>
				     <li><a href="#">ディズニー</a></li>
					<li><a href="#">東京事変</a></li>
				</ul>
			</dd>
		</dl>
	</div>
	<!-- ========== /header ========== -->

	<hr />

	<!-- InstanceBeginEditable name="cat" --><h1>50音検索ページ<!--<img src="../img/theater/title_theater.gif" alt="演劇" width="60" height="60" />--></h1>
<!-- InstanceEndEditable -->

	<!-- ========== main ========== -->
	<div id="main">
	
		<div id ="tx_main_header">	
			<? if($overseas||$figure||$page_figure){
			?>
			<div id ="search_title"><p>洋楽</p></div>	
			<div id = "search_buttons">
			    <ul>
			        <div id ="search_block">
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=ア,あ">ア</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=イ,い">イ</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=ウ,う">ウ</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=エ,え">エ</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=オ,お">オ</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=カ,か">カ</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=キ,き">キ</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=ク,く">ク</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=ケ,け">ケ</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=コ,こ">コ</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=サ,さ">サ</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=シ,し">シ</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=ス,す">ス</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=セ,せ">セ</a></li>
	        			<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=ソ,そ">ソ</a></li>
	        			<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=タ,た">タ</a></li>
	        			<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=チ,ち">チ</a></li>
	        			<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=ツ,つ">ツ</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=テ,て">テ</a></li>
			        	<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=ト,と">ト</a></li>
			        	<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=ナ,な">ナ</a></li>
			        	<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=ニ,に">二</a></li>
			        	<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=ヌ,ぬ">ヌ</a></li>
			        	<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=ネ,ね">ネ</a></li>
			        	<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=ノ,の">ノ</a></li>
			        </div>
			       	<div id ="search_block">
		        		<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=ハ,は">ハ</a></li>
		        		<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=ヒ,ひ">ヒ</a></li>
		        		<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=フ,ふ">フ</a></li>
		        		<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=ヘ,へ">ヘ</a></li>
		        		<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=ホ,ほ">ホ</a></li>
		        		<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=マ,ま">マ</a></li>
		        		<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=ミ,み">ミ</a></li>
		        		<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=ム,む">ム</a></li>
		        		<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=メ,め">メ</a></li>
		        		<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=モ,も">モ</a></li>
		        		<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=ヤ,や">ヤ</a></li>
		        		<li class="space"><a href=""></a></li>
		        		<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=ユ,ゆ">ユ</a></li>
		        		<li class="space"><a href=""></a></li>
		        		<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=ヨ,よ">ヨ</a></li>
		        		<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=ラ,ら">ラ</a></li>
		        		<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=リ,り">リ</a></li>
		        		<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=ル,る">ル</a></li>
		        		<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=レ,れ">レ</a></li>
		        		<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=ロ,ろ">ロ</a></li>
		        		<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=ワ,わ">ワ</a></li>
		        		<li class="space"><a href=""></a></li>
		        		<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=ヲ,を">ヲ</a></li>
		        		<li class="space"><a href=""></a></li>
		        		<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=ン,ん">ン</a></li>
		       	</ul>
		       	<ul>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=A">A</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=B">B</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=C">C</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=D">D</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=E">E</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=F">F</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=G">G</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=H">H</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=I">I</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=J">J</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=K">K</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=L">L</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=M">M</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=N">N</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=O">O</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=P">P</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=Q">Q</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=R">R</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=S">S</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=T">T</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=U">U</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=V">V</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=W">W</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=X">X</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=Y">Y</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?figure=Z">Z</a></li>
			    </ul>
			　　　　　</div>
			<?
			}
			else if($domestic||$moji||$page_moji){
			?>
		            <div id ="search_title"><p>邦楽</p></div>
		            <div id = "search_buttons">
			    <ul>
				    <div id ="search_block">
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=ア,あ">あ</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=イ,い">い</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=ウ,う">う</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=エ,え">え</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=オ,お">お</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=カ,か">か</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=キ,き">き</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=ク,く">く</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=ケ,け">け</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=コ,こ">こ</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=サ,さ">さ</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=シ,し">し</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=ス,す">す</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=セ,せ">せ</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=ソ,そ">そ</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=タ,た">た</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=チ,ち">ち</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=ツ,つ">つ</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=テ,て">て</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=ト,と">と</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=ナ,な">な</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=ニ,に">に</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=ヌ,ぬ">ぬ</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=ネ,ね">ね</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=ノ,の">の</a></li>
				    </div>
				    <div id="search_block">
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=ハ,は">は</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=ヒ,ひ">ひ</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=フ,ふ">ふ</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=ヘ,へ">へ</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=ホ,ほ">ほ</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=マ,ま">ま</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=ミ,み">み</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=ム,む">む</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=メ,め">め</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=モ,も">も</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=ヤ,や">や</a></li>
				        <li class="space"><a href=""></a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=ユ,ゆ">ゆ</a></li>
				        <li class="space"><a href=""></a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=ヨ,よ">よ</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=ラ,ら">ら</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=リ,り">り</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=ル,る">る</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=レ,れ">れ</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=ロ,ろ">ろ</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=ワ,わ">わ</a></li>
				        <li class="space"><a href=""></a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=ヲ,を">を</a></li>
				        <li class="space"><a href=""></a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=ン,ん">ん</a></li>
				    </div>
			    </ul>	
			    <ul>
				    <div id ="search_block">
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=A">A</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=B">B</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=C">C</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=D">D</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=E">E</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=F">F</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=G">G</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=H">H</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=I">I</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=J">J</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=K">K</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=L">L</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=M">M</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=N">N</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=O">O</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=P">P</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=Q">Q</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=R">R</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=S">S</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=T">T</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=U">U</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=V">V</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=W">W</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=X">X</a></li>
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=Y">Y</a></li>
				    </div>
				    <div id ="search_block_z">
				        <li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?moji=Z">Z</a></li>
				    </div>
			    </ul>
			</div>
			<?
			}
			?>
		</div>
	    <div id = "artists">	
		    <div id ="paging">	
		    <?	
			if($moji||$page_moji){
				$delimitor = '/,/';
       			preg_match($delimitor,$moji,$m_matches);
        		preg_match($delimitor,$page_moji,$pm_matches);	
				if($m_matches || $pm_matches ){
					$explode_page_moji = explode(',',$page_moji);
					$explode_moji = explode(',',$moji);
					if(isset($explode_page_moji[1])){?>
			    <p><?= $explode_page_moji[1] ?></p>
					<?}
					if(isset($explode_moji[1])){?>
				<p><?= $explode_moji[1] ?></p>
					<?}
					}else{
						$substr_page_moji = substr($page_moji,-2,-1);
						$substr_moji = substr($moji,-2,-1);
						?>
				<p><?= $substr_page_moji ?></p>
				<p><?= $substr_moji ?></p>
					<?
					}
				}
					if($figure||$page_figure){
						$delimitor = '/,/';
       					preg_match($delimitor,$figure,$f_matches);
        				preg_match($delimitor,$page_figure,$pf_matches);
        				$explode_page_figure = array();	
						if($f_matches || $pf_matches ){
							$explode_page_figure = explode(',',$page_figure);
							$explode_figure = explode(',',$figure);
						}
						else{
							$substr_page_figure = substr($page_figure,-2,-1);
							$substr_figure = substr($figure,-2,-1);
						}
						if(isset($explode_page_figure[1]) && isset($explode_figure[1])&& isset($substr_page_figure) && isset($substr_figure)){
						?>
				<p><?= $explode_page_figure[1] ?></p>
				<p><?= $explode_figure[1] ?></p>
				<p><?= $substr_page_figure ?></p>
				<p><?= $substr_figure ?></p>
						<?}?>
						<!-- $figureがわたってきているときはpage_figureにfigureを入れる　page_figureがわたってきているときは　page_figureをもう一回入れる-->
						<?
						if(isset($_GET['page_figure'])){
							$page_figure=$_GET['page_figure'];
						}
						elseif($_GET['figure']){
							$page_figure=$_GET['figure'];
						}
					}
					?>
				<div id ="pages_link">
					<?
					foreach($pager['navi'][0]['pages'] as $p){
						if(isset($p['text'])) {
							print $p['text'];
						} elseif($p['current']) {
							printf('<b>%s</b>',$p['n']);
						}else{
							if(isset($pager['navi'][0]['goto_page']) && isset($p['n'])){
							    printf('<a href="%s">%s</a>',$pager['navi'][0]['goto_page'].$p['n'],$p['n']);
							}
						}
					}?>
				</div>
		    </div>
		    <div class ="page_artist_border"><img src="../img/common/side_nav_line.gif" width="690" height="2"></div>
		    <div id = "page_artist">	
			        <? 
			        $artist_of_page = array_splice($page_artist_array,($pager['page']-1)*$unit,$unit);
			     	foreach($artist_of_page as $a){?>
				<div id="page_artist_array">
					<a href ="/~katosaori/artist-page/web-contents/pages/artist_detail.php?artist=<?=$a['name']?>"title="<img src = '../img/music/dummy_event.jpg'>"><?=$a['name'] ?></a><br />
				</div>
				    <?}?>
		    </div>
	    </div>
    </div>
</div>
<!-- ========== /main ========== -->

<hr />

<!-- ========== side ========== -->
<div id="side">
	<!-- InstanceBeginEditable name="side" -->
	<div class="sideCategoryGenre">
	<h2>検索</h2>
	<ul>
	<li>
	<form id="form1" name="form1" method="post" action="">
		<input name="textfield" type="text" id="textfield" size="20" value="" onblur="if(this.value=='') this.value='';" onfocus="if(this.value=
='アーティスト名、公演名、会場名など') this.value='';" />
		<input name="imageField" type="image" id="imageField" src="../img/common/header_search_btn.
gif" alt="検索" />			  
	</form></li>

		<li> <a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?&page_moji=ア,あ&page_domestic=1&count_artist=356">邦楽50音順検索</a></li>

		<li><a href="/~katosaori/artist-page/web-contents/pages/gojyuon.php?&page_figure=A&page_overseas=1&count_artist=1490">洋楽ABC検索</a></li>
	</ul>
	</div>
	<div class="sideCategoryGenre">
		<h2>ジャンル一覧</h2>
		<ul>
		<? for($q=0;$q<=12;$q++): ?>
			<li id ='#'><a href ='./genre.php?genre=<?=urlencode($o[$q])?>'><?= htmlspecialchars($o[$q]);?></a></li>
		<? endfor ?>
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
		<dt><img src="../img/common/side_info_title.gif" alt="お知らせ" width="190" height="18" /></dt>
		<dd>
			<ul>
				<li>2011年12月4日(日)　～　2011年12月4日(日)　メン>テナンスを行います</li>
				<li>2011年12月4日(日)　～　2011年12月4日(日)　メン>テナンスを行います</li>
				</ul>
			</dd>
		</dl>
		<!-- InstanceEndEditable -->
		<ul id="sideBtn">
			<li><a href="#"><img src="../img/mypage/btn_use.gif" alt="楽天チケ>ットの使い方" width="202" height="28" /></a></li>
			<li><a href="#"><img src="../img/mypage/btn_favorite.gif" alt="お気
に入りアーティストを登録" width="202" height="28" /></a></li>
			<li><a href="#"><img src="../img/mypage/btn_magazine.gif" alt="メル
マガの購読" width="202" height="28" /></a></li>
		</ul>
	</div>
	<!-- ========== /side ========== -->

	<hr />

	<!-- ========== footer ========== -->
	<div id="grpRakutenLinkArea">
		<ul id="grpSpelinlk">
			<li><a href="#">総合トップ</a></li>
			<li><a href="#">本</a></li>
			<li><a href="#">雑誌</a></li>
			<li><a href="#">DVD・Blu-ray</a></li>
			<li><a href="#">CD</a></li>
			<li><a href="#">ゲーム</a></li>
			<li><a href="#">ソフトウェア</a></li>
			<li class="grpLast"><a href="#">洋書</a></li>
		</ul>

		<dl id="grpKeyword">
			<dt>キーワード</dt>
			<dd>
			<ul>
			<li><a href="#">レストラン検索</a></li>
			<li><a href="#">飲み会・宴会</a></li>
			<li><a href="#">接待</a></li>
			<li><a href="#">個室</a></li>
			<li><a href="#">記念日</a></li>
			</ul>
			</dd>
		</dl>

		<div id="grpFooter">
			<div id="groupServiceFooter">
				<dl class="title">
					<dt>楽天グループのサービス</dt>
					<dd class="allService"><span><a href="http://www.rakuten.co.jp/sitemap/" onclick="s.gclick('sitemap','ftr')">全サービス一覧へ</a></span></dd>
					<dd class="csr"><a href="http://corp.rakuten.co.jp/csr/" rel="nofollow"><img src="//jp.rakuten-static.com/1/im/ci/csr/w80.gif" alt="社会的責任
[CSR]" width="80" height="20" /></a></dd>
				</dl>
				<ul id="selectedService" class="serviceCol3">
					<li><dl>
					<dt><a href="#########" onclick="s.gclick('#########','ftr-rel')">DVD・CDをレンタルする</a></dt>
					<dd>楽天レンタル</dd>
					</dl></li>
					<li><dl>
					<dt><a href="#########" onclick="s.gclick('#########','ftr-rel')">映画・ドラマ・スポーツ動画もっと見る</a></dt>
					<dd>楽天VIDEO</dd>
					</dl></li>
					<li><dl>
					<dt><a href="#########" onclick="s.gclick('#########','ftr-rel')">本・CD・DVDを購入する</a></dt>
					<dd>楽天ブックス</dd>

					</dl></li>
					<!--
					<li><dl>
					<dt><a href="#########" onclick="s.gclick('#########','ftr-rel')">○○○○○○○○○○○○</a></dt>
					<dd>○○○○○○</dd>
					</dl></li>
					-->
				</ul>
				<div id="serviceList">
					<dl>
						<dt>お買物・ポイント</dt>
						<dd><ul>
						<li><a href="http://www.rakuten.co.jp/" onclick="s.gclick('ichiba','ftr')">ショッピング</a></li>
						<li><a href="http://auction.rakuten.co.jp/" onclick="s.gclick('auction','ftr')">オークション</a></li>
						<li><a href="http://books.rakuten.co.jp/" onclick="s.gclick('books','ftr')">本・DVD・CD</a></li>
						<li><a href="http://ebook.rakuten.co.jp/" onclick="s.gclick('ebook','ftr')">電子書籍</a></li>
						<li><a href="http://auto.rakuten.co.jp/" onclick="s.gclick('auto','ftr')">車・バイク</a></li>
						<li><a href="https://selectgift.rakuten.co.jp/" onclick="s.gclick('gift','ftr')">セレクトギフト</a></li>
						<li><a href="http://import.buy.com/" onclick="s.gclick('import','ftr')">個人輸入</a></li>
						<li><a href="http://netsuper.rakuten.co.jp/" onclick="s.gclick('netsuper','ftr')">ネットスーパー</a></li>
						<li><a href="https://my.rakuten.co.jp/" onclick="s.gclick('myrakuten','ftr')">my Rakuten</a></li>
						<li><a href="https://point.rakuten.co.jp/" onclick="s.gclick('point','ftr')">楽天PointClub</a></li>
						<li><a href="http://point-g.rakuten.co.jp/" onclick="s.gclick('pointgallery','ftr')">ポイント特集</a></li>
						<li><a href="http://p-store.rakuten.co.jp/event/pointget/" onclick="s.gclick('pstore','ftr')">ポイント加盟店</a></li>
						</ul>
						</dd>
					</dl>
					<dl>
						<dt>旅行・エンタメ</dt>
						<dd><ul>
						<li><a href="http://travel.rakuten.co.jp/" onclick="s.gclick('travel_dom','ftr')">旅行・ホテル予約・航空券</a></li>
						<li><a href="http://gora.golf.rakuten.co.jp/" onclick="s.gclick('gora','ftr')">ゴルフ場予約</a></li>
						<li><a href="http://ticket.rakuten.co.jp/" onclick="s.gclick('ticket','ftr')">イベント・チケット販売</a></li>

						<li><a href="http://www.rakuteneagles.jp/" onclick="s.gclick('eagles','ftr')">楽天イーグルス</a></li>
						<li><a href="http://rental.rakuten.co.jp/" onclick="s.gclick('rental','ftr')">DVD・CDレンタル</a></li>
						<li><a href="http://www.showtime.jp/isp/rakuten/" onclick="s.gclick('showtime','ftr')">アニメ・映画</a></li>
						<li><a href="http://dl.rakuten.co.jp/" onclick="s.gclick('download','ftr')">ダウンロード</a></li>
						<li><a href="http://keiba.rakuten.co.jp/" onclick="s.gclick('keiba','ftr')">地方競馬</a></li>
						<li><a href="http://uranai.rakuten.co.jp/" onclick="s.gclick('uranai','ftr')">占い</a></li>
						<li><a href="https://toto.rakuten.co.jp/" onclick="s.gclick('toto','ftr')">toto・BIG</a></li>
						<li><a href="http://entertainment.rakuten.co.jp/" onclick="s.gclick('entertainment','ftr')">映画・ドラマ・エンタメ情報</a></li>
						</ul>
						</dd>
					</dl>
					<dl>
						<dt>マネー</dt>
						<dd><ul>
						<li><a href="https://www.rakuten-sec.co.jp/" onclick="s.gclick('sec','ftr')">ネット証券（株・FX・投資信託）</a></li>
						<li><a href="http://www.rakuten-bank.co.jp/" onclick="s.gclick('ebank','ftr')">インターネット銀行</a></li>
						<li><a href="http://www.rakuten-bank.co.jp/loan/cardloan/" onclick="s.gclick('ebank','ftr')">カードローン</a></li>
						<li><a href="http://www.rakuten-card.co.jp/" onclick="s.gclick('kc','ftr')">クレジットカード</a></li>
						<li><a href="http://www.edy.jp/">電子マネー
</a></li>
						<li><a href="http://www.rakuten-bank.co.jp/home-loan/" onclick="s.gclick('ebank','ftr')">住宅ローン</a></li>
