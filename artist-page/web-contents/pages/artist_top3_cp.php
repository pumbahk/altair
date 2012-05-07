<?php
$dbh = mysql_connect("127.0.0.1:3306", "root", 'root');
mysql_selectdb("artistpage");
mysql_set_charset( "UTF8", $dbh );
$l = "select * from g where parent_id = 0";
$d = mysql_query($l,$dbh);
$r=0;
$t = array();
  while($row=mysql_fetch_assoc($d)){
	$t[$r] = $row['genre'];
	$r++;
	}
$rank_set_jap = array();
$rank_set = array();
	$xml_str = file_get_contents('http://api.rakuten.co.jp/rws/3.0/rest?developerId=12657057e6e263dfe5dd57b5565078da&operation=ItemRanking&version=2010-08-05&genreId=200533');
	$xml_str = str_replace('header:Header','Header',$xml_str);
	$xml_str = str_replace('itemRanking:ItemRanking xmlns:itemRanking="http://api.rakuten.co.jp/rws/rest/ItemRanking/2011-12-01"', 'itemRanking', $xml_str);
        $xml_str = str_replace('itemRanking:ItemRanking', 'itemRanking', $xml_str);
	$xml  = simplexml_load_string($xml_str);
	echo "\n";
	for ($x =0;$x<=9;$x++){
		$rank_set_jap[$x+1] =  $xml->Body->itemRanking->Item[$x]->itemName;
		$imgurl_jap[$x+1] = $xml->Body->itemRanking->Item[$x]->smallImageUrl;
		$artist_long_jap[$x+1] = $xml->Body->itemRanking->Item[$x]->itemCaption;
		$artist_jap[$x+1] = explode("発売日",$artist_long_jap[$x+1]);
			
	}
	$xml_str = file_get_contents('http://api.rakuten.co.jp/rws/3.0/rest?developerId=12657057e6e263dfe5dd57b5565078da&operation=ItemRanking&version=2010-08-05&genreId=200534');
        $xml_str = str_replace('header:Header','Header',$xml_str);
        $xml_str = str_replace('itemRanking:ItemRanking xmlns:itemRanking="http://api.rakuten.co.jp/rws/rest/ItemRanking/2011-12-01"', 'itemRanking', $xml_str);
        $xml_str = str_replace('itemRanking:ItemRanking', 'itemRanking', $xml_str);
	$xml  = simplexml_load_string($xml_str);
        echo "\n";
        for ($x =0;$x<=9;$x++){
		$rank_set[$x+1] = $xml->Body->itemRanking->Item[$x]->itemName;
		$imgurl[$x+1] = $xml->Body->itemRanking->Item[$x]->smallImageUrl;
		$artist_long[$x+1] = $xml->Body->itemRanking->Item[$x]->itemCaption;
                $artist[$x+1] = explode("発売日",$artist_long[$x+1]);

        }
?>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transition//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja"><!- InstanceBegin template="/Template/template.dwt" codeOutsideHTMLslocked="false" -->
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<!-- InstanceBeginEditable name="doctitle" --><title>アーティストページ　トップ</title>
<!-- InstanceEndEditable -->
<meta name="description" content="チケットの販売、イベントの予約は楽天チケットで！楽天チケ>ットは演劇、バレエ、ミュージカルなどの舞台、クラシック、オペラ、ロックなどのコンサート、野>球、サッカー、格闘技などのスポーツ、その他イベントなどのチケットのオンラインショッピングサ>イトです。" />
<meta name="keywords" content="チケット,演劇,クラシック,オペラ,コンサート,バレエ,ミュージカル,野球,サッカー,格闘技" />
<meta http-equiv="content-style-type" content="text/css" />
<meta http-equiv="content-script-type" content="text/javascript" />
<link rel="shortcut icon" href="../design/img/common/favicon.ico" />
<link rel="stylesheet" href="../design/html/css/import.css" type="text/css" media="all" />
<link rel="stylesheet" href="import.css" type="text/css" media="all" />
<script type="text/javascript" src="../js/jquery.js">
</script>
<!-- InstanceParam name="id" type="text" value="theater" -->
</head>
<body id="theater">

<p id="naviSkip"><a href="#main" tabindex="1" title="本文へジャンプ"><img src="../img/common/skip.gif" alt="本文へジャンプ" width="1" height="1" /></a></p>

<div id="container">

	<!-- ========== header ========== -->
	<div id="grpheader">
		<p id="tagLine">チケット販売・イベント予約</p>
		<p id="siteID"><a href="http://ticket.rakuten.co.jp/"><img src="../img/common/header_logo_01.gif" alt="楽天チケット" class="serviceLogo" width="97" height="35" /></a><a href="http://ticket.rakuten.co.jp/"><img src="../img/common/header_logo_02.gif" alt="チケット" class="serviceTitle" width="88" height="23" /></a></p>
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
			<li><a href="../index.html"><img src="../img/common/header_nav_top.gif" alt="チケットトップ" width="132" height="40" /></a></li>
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
			<input name="textfield" type="text" id="textfield" size="40" value="アーティスト名、公演名、会場名など" onblur="if(this.value=='') this.value='アーティスト名、公演名、会場名など';" onfocus="if(this.value=='アーティスト名、公演名、会場名など') this.value='';" />
			<input name="imageField" type="image" id="imageField" src="../img/common/header_search_btn.gif" alt="検索" />
			<a href="#">詳細検索</a>
		</form>
		<dl>
			<dt><img src="../img/common/header_search_hot.gif" alt="ホットワード" width="50" height="45" /></dt>
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
	
	<!-- InstanceBeginEditable name="cat" --><h1><img src="../img/theater/title_theater.gif" alt="演劇" width="60" height="60" /></h1>
<!-- InstanceEndEditable -->
	
	<!-- ========== main ========== -->
	<div id="main">
		<!-- InstanceBeginEditable name="main" -->
		<ul id="attention">
			<li>【注目!!】<a href="#">ポイント10倍キャンペーン実施中！『大相撲三月場所』マス席の他、希少な溜まり席も販売！</a></li>
			<li>【注目!!】<a href="#">きゃりーぱみゅぱみゅ、倖田來未 、CNBLUE ら出演♪「オンタマカーニバル2012」1/14発売！</a></li>
		</ul>
		<div id="slideShow">
			<p><img src="../img/music/dummy_slideshow.jpg" width="742" height="344" /></p>
		</div>
		<h2><img src="../img/theater/title_topics.gif" alt="トピックス" width="742" height="43" /></h2>
		<ul id="topics">
			<li><a href="#">ポイント10倍キャンペーン実施中！『大相撲三月場所』マス席の他、希少な溜まり席も販売！</a></li>
			<li><a href="#">きゃりーぱみゅぱみゅ、倖田來未 、CNBLUE ら出演♪「オンタマカーニバル2012」1/14発売！</a></li>
			<li><a href="#">47年ぶりに日本上陸のツタンカーメン展！1/31購入分まで、もれなくポイント10倍！</a></li>
			<li><a href="#">東京、大阪で過去最高の動員を記録したKOOZAが福岡へ上陸！楽チケならポイント10倍！</a></li>
		</ul>
		<h2><img src="../img/theater/title_event.gif" alt="注目のイベント" width="742" height="43" /></h2>
		<script type="text/javascript" src="../js/jquery.flatheights.js"></script>
		<script type="text/javascript">
		$(function() {
			var sets = [], temp = [];
			$('.event').each(function(i) {
				temp.push(this);
				if (i % 2 == 1) {
					sets.push(temp);
					temp = [];
				}
			});
			if (temp.length) sets.push(temp);
			$.each(sets, function() {
				$(this).flatHeights();
			});
		});
		</script>
		<div class="event">
			<dl>
				<dt><a href="#">ソ・ジソブ　日本公式ファンクラブ1周年記念！2012 ファンミーティング in 東京</a></dt>
				<dd>2011年12月4日(日)　〜　2011年12月4日(日)　幕張メッセイベントホール 2011年12月4日(日)　〜</dd>
			</dl>
			<p><a href="#"><img src="../img/music/dummy_event.jpg" alt="" width="80" height="80" /></a><br />
			<a href="#">あと2日</a></p>
		</div>
		<div class="event">
			<dl>
				<dt><a href="#">ソ・ジソブ　日本公式ファンクラブ1周年記念！2012 ファンミーティング in 東京</a></dt>
				<dd>2011年12月4日(日)　〜　2011年12月4日(日)　幕張メッセイベントホール 2011年12月4日(日)　〜</dd>
			</dl>
			<p><a href="#"><img src="../img/music/dummy_event.jpg" alt="" width="80" height="80" /></a><br />
			<a href="#">あと2日</a></p>
		</div>
		<div class="event">
			<dl>
				<dt><a href="#">ソ・ジソブ　日本公式ファンクラブ1周年記念！2012 ファンミーティング in 東京</a></dt>
				<dd>2011年12月4日(日)　〜　2011年12月4日(日)　幕張メッセイベントホール 2011年12月4日(日)　〜2011年12月4日(日)　〜　2011年12月4日(日)　幕張メッセイベントホール 2011年12月4日(日)　〜</dd>
			</dl>
			<p><a href="#"><img src="../img/music/dummy_event.jpg" alt="" width="80" height="80" /></a><br />
			<a href="#">あと2日</a></p>
		</div>
		<div class="event">
			<dl>
				<dt><a href="#">ソ・ジソブ　日本公式ファンクラブ1周年記念！2012 ファンミーティング in 東京</a></dt>
				<dd>2011年12月4日(日)　〜　2011年12月4日(日)　幕張メッセイベントホール 2011年12月4日(日)　〜</dd>
			</dl>
			<p><a href="#"><img src="../img/music/dummy_event.jpg" alt="" width="80" height="80" /></a><br />
			<a href="#">あと2日</a></p>
		</div>
		<div class="event">
			<dl>
				<dt><a href="#">ソ・ジソブ　日本公式ファンクラブ1周年記念！2012 ファンミーティング in 東京</a></dt>
				<dd>2011年12月4日(日)　〜　2011年12月4日(日)　幕張メッセイベントホール 2011年12月4日(日)　〜</dd>
			</dl>
			<p><a href="#"><img src="../img/music/dummy_event.jpg" alt="" width="80" height="80" /></a><br />
			<a href="#">あと2日</a></p>
		</div>
		<div class="event">
			<dl>
				<dt><a href="#">ソ・ジソブ　日本公式ファンクラブ1周年記念！2012 ファンミーティング in 東京</a></dt>
				<dd>2011年12月4日(日)　〜　2011年12月4日(日)　幕張メッセイベントホール 2011年12月4日(日)　〜</dd>
			</dl>
			<p><a href="#"><img src="../img/music/dummy_event.jpg" alt="" width="80" height="80" /></a><br />
			<a href="#">あと2日</a></p>
		</div>
		<div class="event">
			<dl>
				<dt><a href="#">ソ・ジソブ　日本公式ファンクラブ1周年記念！2012 ファンミーティング in 東京</a></dt>
				<dd>2011年12月4日(日)　〜　2011年12月4日(日)　幕張メッセイベントホール 2011年12月4日(日)　〜</dd>
			</dl>
			<p><a href="#"><img src="../img/music/dummy_event.jpg" alt="" width="80" height="80" /></a><br />
			<a href="#">あと2日</a></p>
		</div>
		<div class="event">
			<dl>
				<dt><a href="#">ソ・ジソブ　日本公式ファンクラブ1周年記念！2012 ファンミーティング in 東京</a></dt>
				<dd>2011年12月4日(日)　〜　2011年12月4日(日)　幕張メッセイベントホール 2011年12月4日(日)　〜</dd>
			</dl>
			<p><a href="#"><img src="../img/music/dummy_event.jpg" alt="" width="80" height="80" /></a><br />
			<a href="#">あと2日</a></p>
		</div>
		<div id="thisWeek">
			<h2><img src="../img/music/title_thisweek.gif" alt="今週発売のチケット" width="362" height="40" /></h2>
			<p><a href="#">ソ・ジソブ　日本公式ファンクラブ1周年記念2012 ファンミーティング in 東京</a> / <a href="#">ソ・ジソブ　日本公式ファンクラブ1周年記念2012 ファンミーティング in 東京</a> / <a href="#">ソ・ジソブ　日本公式ファンクラブ1周年記念2012 ファンミーティング in 東京</a> / <a href="#">ソ・ジソブ　日本公式ファンクラブ1周年記念2012 ファンミーティング in 東京</a> / <a href="#">ソ・ジソブ　日本公式ファンクラブ1周年記念2012 ファンミーティング in 東京</a> / <a href="#">ソ・ジソブ　日本公式ファンクラブ1周年記念2012 ファンミーティング in 東京</a> / <a href="#">ソ・ジソブ　日本公式ファンクラブ1周年記念2012 ファンミーティング in 東京</a> / </p>
		</div>
		<div id="nearTheEnd">
			<h2><img src="../img/music/title_neartheend.gif" alt="販売終了間近" width="362" height="40" /></h2>
			<p><a href="#">ソ・ジソブ　日本公式ファンクラブ1周年記念2012 ファンミーティング in 東京</a> / <a href="#">ソ・ジソブ　日本公式ファンクラブ1周年記念2012 ファンミーティング in 東京</a> / <a href="#">ソ・ジソブ　日本公式ファンクラブ1周年記念2012 ファンミーティング in 東京</a> / <a href="#">ソ・ジソブ　日本公式ファンクラブ1周年記念2012 ファンミーティング in 東京</a> / <a href="#">ソ・ジソブ　日本公式ファンクラブ1周年記念2012 ファンミーティング in 東京</a> / <a href="#">ソ・ジソブ　日本公式ファンクラブ1周年記念2012 ファンミーティング in 東京</a> / <a href="#">ソ・ジソブ　日本公式ファンクラブ1周年記念2012 ファンミーティング in 東京</a> / </p>
		</div>
		
		<script type="text/javascript" src="../js/jquery.jcarousel.js"></script>
		<script type="text/javascript">
		$(function() {
			$('#checkEvent ul').jcarousel({scroll:7});
		});
		</script>
		<div id="checkEvent">
			<h2><img src="../img/music/title_check.gif" alt="最近チェックしたイベント" width="748" height="37" /></h2>
			<ul>
				<li><a href="#"><img src="../img/music/dummy_check.jpg" alt="" width="80" height="80" /></a><br />
				<a href="#">公演名公演名公演名1</a></li>
				<li><a href="#"><img src="../img/music/dummy_check.jpg" alt="" width="80" height="80" /></a><br />
				<a href="#">公演名2</a></li>
				<li><a href="#"><img src="../img/music/dummy_check.jpg" alt="" width="80" height="80" /></a><br />
				<a href="#">公演名公演名公演名公演名3</a></li>
				<li><a href="#"><img src="../img/music/dummy_check.jpg" alt="" width="80" height="80" /></a><br />
				<a href="#">公演名4</a></li>
				<li><a href="#"><img src="../img/music/dummy_check.jpg" alt="" width="80" height="80" /></a><br />
				<a href="#">公演名5</a></li>
				<li><a href="#"><img src="../img/music/dummy_check.jpg" alt="" width="80" height="80" /></a><br />
				<a href="#">公演名公演名公演名6</a></li>
				<li><a href="#"><img src="../img/music/dummy_check.jpg" alt="" width="80" height="80" /></a><br />
				<a href="#">公演名公演名7</a></li>
				<li><a href="#"><img src="../img/music/dummy_check.jpg" alt="" width="80" height="80" /></a><br />
				<a href="#">公演名公演名8</a></li>
				<li><a href="#"><img src="../img/music/dummy_check.jpg" alt="" width="80" height="80" /></a><br />
				<a href="#">公演名9</a></li>
				<li><a href="#"><img src="../img/music/dummy_check.jpg" alt="" width="80" height="80" /></a><br />
				<a href="#">公演名公演名10</a></li>
			</ul>
			<p class="align1"><a href="#">もっと見る</a></p>
		</div>
		<!-- InstanceEndEditable -->
	</div>
	<!-- ========== /main ========== -->
	
	<hr />
	
	<!-- ========== side ========== -->
	<div id="side">
		<!-- InstanceBeginEditable name="side" -->
		<div class="sideCategoryGenre">
		<h2>特集</h2>
		<ul>
			<li><a href="#">特集/ライブハウスへ行こう!!</a></li>
			<li><a href="#">ロックフェス特集</a></li>
			<li><a href="#">アニメぴあ</a></li>
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
			<dt><img src="../img/common/side_info_title.gif" alt="お知らせ" width="190" height="18" /></dt>
			<dd>
				<ul>
					<li>2011年12月4日(日)　～　2011年12月4日(日)　メンテナンスを行います</li>
					<li>2011年12月4日(日)　～　2011年12月4日(日)　メンテナンスを行います</li>
				</ul>
			</dd>
		</dl>
		<!-- InstanceEndEditable -->
		<ul id="sideBtn">
			<li><a href="#"><img src="../img/mypage/btn_use.gif" alt="楽天チケットの使い方" width="202" height="28" /></a></li>
			<li><a href="#"><img src="../img/mypage/btn_favorite.gif" alt="お気に入りアーティストを登録" width="202" height="28" /></a></li>
			<li><a href="#"><img src="../img/mypage/btn_magazine.gif" alt="メルマガの購読" width="202" height="28" /></a></li>
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
					<dd class="csr"><a href="http://corp.rakuten.co.jp/csr/" rel="nofollow"><img src="//jp.rakuten-static.com/1/im/ci/csr/w80.gif" alt="社会的責任[CSR]" width="80" height="20" /></a></dd>
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
						<li><a href="http://www.edy.jp/">電子マネー</a></li>
						<li><a href="http://www.rakuten-bank.co.jp/home-loan/" onclick="s.gclick('ebank','ftr')">住宅ローン</a></li>
						<li><a href="http://hoken.rakuten.co.jp/" onclick="s.gclick('hoken','ftr')">生命保険・損害保険</a></li>
						<li><a href="http://money.rakuten.co.jp/" onclick="s.gclick('money','ftr')">マネーサービス一覧</a></li>
						</ul>
						</dd>
					</dl>
					<dl>
						<dt>暮らし・情報</dt>
						<dd><ul>
						<li><a href="http://www.infoseek.co.jp/" onclick="s.gclick('is','ftr')">ニュース・検索</a></li>
						<li><a href="http://plaza.rakuten.co.jp/" onclick="s.gclick('blog','ftr')">ブログ</a></li>
						<li><a href="http://delivery.rakuten.co.jp/" onclick="s.gclick('delivery','ftr')">出前・宅配・デリバリー</a></li>
						<li><a href="http://dining.rakuten.co.jp/" onclick="s.gclick('dining','ftr')">グルメ・外食</a></li>
						<li><a href="http://recipe.rakuten.co.jp" onclick="s.gclick('recipe','ftr')">レシピ</a></li>
						<li><a href="http://www.nikki.ne.jp/" onclick="s.gclick('minshu','ftr')">就職活動</a></li>
						<li><a href="http://career.rakuten.co.jp/" onclick="s.gclick('carrer','ftr')">仕事紹介</a></li>
						<li><a href="http://realestate.rakuten.co.jp/"  onclick="s.gclick('is:house','ftr')">不動産情報</a></li>
						<li><a href="http://onet.rakuten.co.jp/" onclick="s.gclick('onet','ftr')">結婚相談所</a></li>
						<li><a href="http://wedding.rakuten.co.jp/" onclick="s.gclick('wedding','ftr')">結婚式場情報</a></li>
						<li><a href="http://shashinkan.rakuten.co.jp/" onclick="s.gclick('shashinkan','ftr')">写真プリント</a></li>
						<li><a href="http://nuigurumi.ynot.co.jp/" onclick="s.gclick('nuigurumi','ftr')">ぬいぐるみ電報</a></li>
						<li><a href="http://greeting.rakuten.co.jp/" onclick="s.gclick('greeting','ftr')">グリーティングカード</a></li>
						<li><a href="http://broadband.rakuten.co.jp/" onclick="s.gclick('broadband','ftr')">プロバイダ・インターネット接続</a></li>
						</ul>
						</dd>
					</dl>
					<dl>
						<dt>ビジネス</dt>
						<dd><ul>
						<li><a href="http://business.rakuten.co.jp/" onclick="s.gclick('business','ftr')">ビジネス見積り</a></li>
						<li><a href="http://research.rakuten.co.jp/" onclick="s.gclick('research','ftr')">リサーチ</a></li>
						<li><a href="http://affiliate.rakuten.co.jp/" onclick="s.gclick('affiliate','ftr')">アフィリエイト</a></li>
						<li><a href="http://checkout.rakuten.co.jp/biz/" onclick="s.gclick('checkout','ftr')">決済システム</a></li>
						</ul>
						</dd>
					</dl>
				</div><!-- /div#serviceList -->
			</div><!-- /div#groupServiceFooter -->
			<div id="companyFooter">
				<ul>
					<li><a href="http://corp.rakuten.co.jp/" rel="nofollow">会社概要</a></li>
					<li><a href="http://privacy.rakuten.co.jp/" rel="nofollow">個人情報保護方針</a></li>
					<li><a href="http://corp.rakuten.co.jp/csr/">社会的責任[CSR]</a></li>
					<li class="grpLast"><a href="http://www.rakuten.co.jp/recruit/">採用情報</a></li>
				</ul>
				<p id="copyright">Copyright &copy; 1997-2011 Rakuten, Inc. All Rights Reserved.</p>
			</div><!-- /div#companyFooter -->
		</div><!-- /div#grpFooter -->
	</div><!-- /div#grpRakutenLinkArea -->
	<!-- ========== /footer ========== -->

<!-- /container --></div>

</body>
<!-- InstanceEnd --></html>