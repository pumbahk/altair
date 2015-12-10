<?php

include 'config.php';
include 'artist_detail_function.php';
$result = artist_detail_function();
extract($result);

?>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transition//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja"><!- InstanceBegin template="/Template/template.dwt" codeOutsideHTMLslocked="false" -->
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<!-- InstanceBeginEditable name="doctitle" --><title>アーティストページ　トップ</title>
<!-- InstanceEndEditable -->
<meta name="description" content="チケットの販売、イベントの予約は楽天チケットで！楽天チケ>ットは演劇、バレエ、ミュージカルな>どの舞台、クラシック、オペラ、ロックなどのコンサート、野>球、サッカー、格闘技などのスポーツ、その他イベントなどのチケットのオ>ンラインショッピングサ>イトです。" />
<meta name="keywords" content="チケット,演劇,クラシック,オペラ,コンサート,バレエ,ミュージカル,野球,サッカー,格闘技" />

<link href="./css/jquery.mCustomScrollbar.css" rel="stylesheet" type="text/css" />
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta http-equiv="content-style-type" content="text/css" />
<meta http-equiv="content-script-type" content="text/javascript" />
<link rel="shortcut icon" href="../design/img/common/favicon.ico" />
<link rel="stylesheet" href="./css/import.css" type="text/css" media="all" />
<link rel="stylesheet" href="./css/artist_detail.css" type ="text/css" media="all" />
<script type="text/javascript" src="http://www.google.com/jsapi"></script>
<script type="text/javascript">google.load("jquery", "1.4");</script>
<script type="text/javascript" src="./js/cdshousai.js"></script>
<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.12/jquery-ui.js"></script>
<script type="text/javascript" src="./js/jquery.easing.1.3.js"></script>
<script type="text/javascript" src="./js/jquery.mousewheel.min.js"></script>
<!-- InstanceParam name="id" type="text" value="theater" -->

</head>
<body id="theater">
<p id="naviSkip"><a href="#main" tabindex="1" title="本文へジャンプ"><img src="../img/common/skip.gif" alt="本文へジャンプ" width="1" height="1" /></a></p>
<div id="container">
	<!-- ========== header ========== -->
	<div id="grpheader">
		<p id="tagLine">チケット販売・イベント予約</p>
		<p id="siteID"><a href="http://ticket.rakuten.co.jp/"><img src="../img/common/header_logo_01.gif" alt="楽天チ>ケット" class="serviceLogo" width="97" height="35" /></a><a href="http://ticket.rakuten.co.jp/"><img src="../img/common/header_logo_02.gif" alt="チケット" class="serviceTitle" width="88" height="23" /></a></p>
		<dl id="remoteNav">
		<dt>楽天グループ関連</dt>
		<dd class="grpRelation">
		<ul><!---->
			<li id="grpNote"><noscript><a href="https://card.rakuten.co.jp/entry/">今すぐ2,000ポイント>！</a></noscript></li><!---->
			<li><a href="#">必見！5,000ポイントがもらえる</a></li><!---->
			<li class="grpHome"><a href="http://www.rakuten.co.jp/">楽天市場へ</a></li><!----></ul>
			<script type="text/javascript" src="//jp.rakuten-static.com/1/js/lib/prm_selector.js"></script>
			<script type="text/javascript" src="//jp.rakuten-static.com/1/js/grp/hdr/prm_sender.js"></script>
			</dd>
			<dt>補助メニュー</dt>
			<dd class="siteUtility">
			<ul><!---->
			<li><a href="#">初めての方へ</a></li><!---->
			<li><a href="#">公演中止・変更情報</a></li><!---->
			<li><a href="#">ヘルプ</a></li><!---->
			<li class="last"><a href="#">サイトマップ</a></li><!---->
			</ul>
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
		<input name="textfield" type="text" id="textfield" size="40" value="アーティスト名、公演名、会場名など
" onblur="if(this.value=='') this.value='アーティスト名、公演名、会場名など';" onfocus="if(this.value=='アーティスト名、公演名
、会場名など') this.value='';" />
		<input name="imageField" type="image" id="imageField" src="../img/common/header_search_btn.gif" alt=">検索" />
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

	<!-- InstanceBeginEditable name="cat" -->
<!-- InstanceEndEditable -->

	<!-- ========== main ========== -->
<div id ="main">
	<div id ="main_bg">
		<div id ="main_center">
			<div id ="plof_box">
				<div id ="artistname"><p><?= $artist_name ?></p></div>	
				<center><div id ="picture">
				</div></center>
				<?php
				if($plofs){
					echo "<div id ='plof'>".$plofs."</div>";
				}
				else{
					echo "<div id ='plof'>プロフィール情報がありません</div>";
				}
				?>
			</div><!--plof_box-->
		</div><!--main_center-->
	
		<div id="main_right">
			<div id ="discography_title"><p>ディスコグラフィ</p></div>
				<div id="mcs_container">
					<div class="customScrollBox">
						<div class="scroll_container">
							<div class="scroll_content">
								<?php for($o = 0; $o <= $count; $o++){ ?>
									<dl>
										<dt><img src="<?= $photo[$o]['photo'] ?>"></dt>
										    <?if(isset($photo[$o]['salesDate'])){?>
											    <dd><?= $photo[$o]['salesDate'] ?></dd>
											    <dd><a href="/~katosaori/altair-devel/altair/artist-page/web-contents/pages/cd.php?photo=<?=urlencode($photo[$o]['photo']);?>"><?= $photo[$o]['cdname'] ?></a></dd>
                                            <?}?>
									</dl>
								<?php }?>
							</div>
						</div>
					<div class="dragger_container">
				<div class="dragger"></div>
			</div>
			<a href="#" class="scrollUpBtn"></a> <a href="#" class="scrollDownBtn"></a>
		</div>
	</div>	  

	<!-- content block -->
	<script>
		$(window).load(function() {
			mCustomScrollbars();
		});
		function mCustomScrollbars(){
		/* 
		malihu custom scrollbar function parameters: 
		1) scroll type (values: "vertical" or "horizontal")
		2) scroll easing amount (0 for no easing) 
		3) scroll easing type 
		4) extra bottom scrolling space for vertical scroll type only (minimum value: 1)
		5) scrollbar height/width adjustment (values: "auto" or "fixed")
		6) mouse-wheel support (values: "yes" or "no")
		7) scrolling via buttons support (values: "yes" or "no")
		8) buttons scrolling speed (values: 1-20, 1 being the slowest)
		*/
		$("#mcs_container").mCustomScrollbar("vertical",300,"easeOutCirc",1.05,"auto","yes","yes",15); 
		}

		/* function to fix the -10000 pixel limit of jquery.animate */
		$.fx.prototype.cur = function(){
		if ( this.elem[this.prop] != null && (!this.elem.style || this.elem.style[this.prop] == null) ) {return this.elem[ this.prop ]; }
			var r = parseFloat( jQuery.css( this.elem, this.prop ) );
			return typeof r == 'undefined' ? 0 : r;
		}

		/* function to load new content dynamically */
		function LoadNewContent(id,file){
			$("#"+id+" .customScrollBox .scroll_content").load(file,function(){
				mCustomScrollbars();
			});
		}
	</script>
	<script src="./js/jquery.mCustomScrollbar.js"></script>
	<script charset="utf-8" src="http://widgets.twimg.com/j/2/widget.js"></script>
	<script>
		new TWTR.Widget({
		version: 2,
		type: 'search',
		search: '<?= $artist_name ?>',
		interval: 30000,
		title: '<?= $artist_name."に関するツイート" ?>',
		subject: '',
		width: 237,
		height: 300,
		theme: {
		  	shell: {
				background: '#8ec1da',
				color: '#ffffff'
			},
			tweets: {
				background: '#ffffff',
				color: '#444444',
				links: '#1985b5'
			}
		},
		features: {
			scrollbar: false,
			loop: true,
			live: true,
			behavior: 'default'
		}
		}).render().start();
	</script>


	</div>
	<div id ="main_all">
		<div id ='title_check'></div>
			<div id='carousel_container'>
				<div id='left_scroll'></div>
					<div id='carousel_inner' style="height:100px;">
						<ul id='carousel_ul'>
						 <?php
							if(isset($photo) && isset($count_photos)){
								for($o = 0; $o <= $count_photos; $o++){
									$pattern = '/noimage/';
									preg_match ($pattern,$photo[$o]['largeImage'],$matches);
									if (empty($matches)){?>
										<li onclick="ReWrite(<?= $dvd_img[$o] ?>)"><a href="/~katosaori/altair-devel/altair/artist-page/web-contents/pages/cd.php?photo=<?=urlencode($photo[$o]['photo']);?>"><img src='<?= $dvd_img[$o] ?>' /></a></li>
									<?php }
								}
							}	
							else{
								echo "CD画像がありません";
							}?>
						</ul> 
					</div> 
					<div id='right_scroll'></div>
				</div>
			</div>
		</div>
	</div>
	
<!-- ======= /main ========== -->

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

		<li> <a href="/~katosaori/altair-devel/altair/artist-page/web-contents/pages/gojyuon.php?page_moji=ア,あ&page_domestic=1&count_artist=356">邦楽50音順検索</a></li>
		<li><a href="/~katosaori/altair-devel/altair/artist-page/web-contents/pages/gojyuon.php?page_figure=A&page_overseas=1&count_artist=1490">洋楽ABC検索</a></li>

	</ul>

		</div>
		<div class="sideCategoryGenre">
		<h2>ジャンル一覧</h2>
		<ul>
 
		<? for($q=0;$q<=12;$q++): ?>

		<li id ='#'><a href ='./genre.php?genre=<?=urlencode($p[$q])?>'><?= htmlspecialchars($p[$q]); ?></a></li>
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
					<dt><a href="#########" onclick="s.gclick('#########','ftr-rel')">DVD・CDをレンタルす>る</a></dt>
					<dd>楽天レンタル</dd>
					</dl></li>
					<li><dl>
					<dt><a href="#########" onclick="s.gclick('#########','ftr-rel')">映画・ドラマ・スポー
ツ動画もっと見る</a></dt>
					<dd>楽天VIDEO</dd>
					</dl></li>
					<li><dl>
					<dt><a href="#########" onclick="s.gclick('#########','ftr-rel')">本・CD・DVDを購入す>る</a></dt>
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
						<li><a href="http://www.rakuten.co.jp/" onclick="s.gclick('ichiba','ftr')">シ>ョッピング</a></li>
						<li><a href="http://auction.rakuten.co.jp/" onclick="s.gclick('auction','ftr')">オークション</a></li>
						<li><a href="http://books.rakuten.co.jp/" onclick="s.gclick('books','ftr')">本
・DVD・CD</a></li>
						<li><a href="http://ebook.rakuten.co.jp/" onclick="s.gclick('ebook','ftr')">電
子書籍</a></li>
						<li><a href="http://auto.rakuten.co.jp/" onclick="s.gclick('auto','ftr')">車・
バイク</a></li>
						<li><a href="https://selectgift.rakuten.co.jp/" onclick="s.gclick('gift','ftr')">セレクトギフト</a></li>
						<li><a href="http://import.buy.com/" onclick="s.gclick('import','ftr')">個人輸
入</a></li>
						<li><a href="http://netsuper.rakuten.co.jp/" onclick="s.gclick('netsuper','ftr')">ネットスーパー</a></li>
						<li><a href="https://my.rakuten.co.jp/" onclick="s.gclick('myrakuten','ftr')">my Rakuten</a></li>
						<li><a href="https://point.rakuten.co.jp/" onclick="s.gclick('point','ftr')">>楽天PointClub</a></li>
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
						<li><a href="http://dl.rakuten.co.jp/" onclick="s.gclick('download','ftr')">ダ
ウンロード</a></li>
						<li><a href="http://keiba.rakuten.co.jp/" onclick="s.gclick('keiba','ftr')">地
方競馬</a></li>
						<li><a href="http://uranai.rakuten.co.jp/" onclick="s.gclick('uranai','ftr')">占い</a></li>
						<li><a href="https://toto.rakuten.co.jp/" onclick="s.gclick('toto','ftr')">toto・BIG</a></li>
						<li><a href="http://entertainment.rakuten.co.jp/" onclick="s.gclick('entertainment','ftr')">映画・ドラマ・エンタメ情報</a></li>
						</ul>
						</dd>
					</dl>
					<dl>
						<dt>マネー</dt>
						<dd><ul>
						<li><a href="https://www.rakuten-sec.co.jp/" onclick="s.gclick('sec','ftr')">>ネット証券（株・FX・投資信託）</a></li>
						<li><a href="http://www.rakuten-bank.co.jp/" onclick="s.gclick('ebank','ftr')">インターネット銀行</a></li>
						<li><a href="http://www.rakuten-bank.co.jp/loan/cardloan/" onclick="s.gclick('ebank','ftr')">カードローン</a></li>
						<li><a href="http://www.rakuten-card.co.jp/" onclick="s.gclick('kc','ftr')">ク
レジットカード</a></li>
						<li><a href="http://www.edy.jp/">電子マネー</a></li>
						<li><a href="http://www.rakuten-bank.co.jp/home-loan/" onclick="s.gclick('ebank','ftr')">住宅ローン</a></li>
						<li><a href="http://hoken.rakuten.co.jp/" onclick="s.gclick('hoken','ftr')">生
命保険・損害保険</a></li>
						<li><a href="http://money.rakuten.co.jp/" onclick="s.gclick('money','ftr')">マ
ネーサービス一覧</a></li>
						</ul>
						</dd>
					</dl>
					<dl>
						<dt>暮らし・情報</dt>
						<dd><ul>
						<li><a href="http://www.infoseek.co.jp/" onclick="s.gclick('is','ftr')">ニュー
ス・検索</a></li>
						<li><a href="http://plaza.rakuten.co.jp/" onclick="s.gclick('blog','ftr')">ブ>ログ</a></li>
						<li><a href="http://delivery.rakuten.co.jp/" onclick="s.gclick('delivery','ftr')">出前・宅配・デリバリー</a></li>
						<li><a href="http://dining.rakuten.co.jp/" onclick="s.gclick('dining','ftr')">グルメ・外食</a></li>
						<li><a href="http://recipe.rakuten.co.jp" onclick="s.gclick('recipe','ftr')">>レシピ</a></li>
						<li><a href="http://www.nikki.ne.jp/" onclick="s.gclick('minshu','ftr')">就職>活動</a></li>
						<li><a href="http://career.rakuten.co.jp/" onclick="s.gclick('carrer','ftr')">仕事紹介</a></li>
						<li><a href="http://realestate.rakuten.co.jp/"	onclick="s.gclick('is:house','ftr')">不動産情報</a></li>
						<li><a href="http://onet.rakuten.co.jp/" onclick="s.gclick('onet','ftr')">結婚
相談所</a></li>
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
				<p id="copyright">&copy; Rakuten, Inc.</p>
			</div><!-- /div#companyFooter -->
		</div><!-- /div#grpFooter -->
	</div><!-- /div#grpRakutenLinkArea -->
	<!-- ========== /footer ========== -->

<!-- /container --></div>

<script>
$(window).load(function() {
	$("#mcs_container").mCustomScrollbar("vertical",400,"easeOutCirc",1.05,"auto","yes","yes",10);
});
</script>
<script src="jquery.mCustomScrollbar.js" type="text/javascript"></script>
</body>
<!-- InstanceEnd --></html>


