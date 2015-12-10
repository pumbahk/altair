<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja">
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<title>楽天チケット</title>
<meta http-equiv="content-style-type" content="text/css" />
<meta http-equiv="content-script-type" content="text/javascript" />
<link rel="shortcut icon" href="assets/favicon.ico" />
<link rel="stylesheet" href="assets/import.css" type="text/css" media="all" />
<script type="text/javascript" src="assets/jquery.js"></script>
</head>
<body id="index">
<div id="container">
	<!-- ========== header ========== -->
	<div id="grpheader" style="height:80px">
		<p id="tagLine">チケット販売・イベント予約</p>
		<div id="siteID">
          <div id="logobox" style="width: 100px; float: left">
            <a href="http://ticket.rakuten.co.jp/"><img src="assets/logo.gif" alt="楽天チケット" width="113" height="57" /></a>
          </div>
          <div id="pointbox" style="width: 300px; float: right">
            チケットの購入で楽天ポイントが<br />
            <span style="color: crimson;font-weight:bold">100円</span>ごとに<span style="color: crimson;font-weight:bold">1ポイント</span>貯まります♪
          </div>
        </div>
		<dl id="remoteNav">
		  <dt>楽天グループ関連</dt>
		  <dd class="grpRelation">
			<ul>
			  <li id="grpNote">
				<noscript>
				  <a href="https://card.rakuten.co.jp/entry/">今すぐ2,000ポイント！</a>
				</noscript>
			    </li>
			   <li class="grpHome"><a href="http://www.rakuten.co.jp/">楽天市場へ</a></li>
			 </ul>
			<script type="text/javascript" src="//jp.rakuten-static.com/1/js/lib/prm_selector.js"></script>
			<script type="text/javascript" src="//jp.rakuten-static.com/1/js/grp/hdr/prm_sender.js"></script>
		  </dd>
		  <dt>補助メニュー</dt>
		  <dd class="siteUtility">
			<ul>
   	       </ul>
		  </dd>
		</dl>
    </div>
	<div id="globalNav">
		<ul id="globalNav1">
			<li><a href="#"><img src="assets/header_nav_top_active.jpg" alt="チケットトップ" width="132" height="38" /></a></li>
			<li><a href="#"><img src="assets/header_nav_music.jpg" alt="音楽" width="68" height="38" /></a></li>
			<li><a href="#"><img src="assets/header_nav_stage.jpg" alt="演劇" width="136" height="38" /></a></li>
			<li><a href="#"><img src="assets/header_nav_sports.jpg" alt="スポーツ" width="92" height="38" /></a></li>
			<li><a href="#"><img src="assets/header_nav_event.jpg" alt="イベント・その他" width="146" height="38" /></a></li>
		</ul>
		<ul id="globalNav2">
			<li><a href="#">抽選申込履歴</a></li>
			<li><a href="#">購入履歴</a></li>
			<li><a href="#">お気に入り</a></li>
			<li><a href="#">マイページ</a></li>
		</ul>
	</div>
	<div id="headerSearch" style="height: 10px">
		<dl>
			<dt></dt>
			<dd>
			</dd>
		</dl>
	</div>
	<!-- ========== /header ========== -->
	
	<hr />

	<!-- ========== main ========== -->
	<div id="main">
    <h2>ただいまメンテナンス中です</h2>
    <div class="formWrapper">
      <table cellpadding="0" cellspacing="0" class="form">
        <colgroup>
        </colgroup>
        <tbody>
          <tr>
            <td>
              <?php include_once '../#common/maintenance_message_rt.php'; ?>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
	</div>
	<!-- ========== /main ========== -->
	
	<hr />
	
	<!-- ========== side ========== -->
	<div id="side">

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
			<li><a href="http://www.ticketstar.jp/">運営会社</a></li>
			<li><a href="https://ticket.rakuten.co.jp/inquiry">お問い合わせ</a></li>
			<li><a href="http://privacy.rakuten.co.jp/">個人情報保護方針</a></li>
			<li class="grpLast"><a href="http://www.ticketstar.jp/legal">特定商取引法に基づく表示</a></li>
		  </ul>
		  <p id="copyright">&copy; TicketStar, Inc. </p>
		</div><!-- /div#companyFooter -->
	  </div><!-- /div#grpFooter -->
	</div><!-- /div#grpRakutenLinkArea -->
	<!-- ========== /footer ========== -->

<!-- /container --></div>

</body>
</html>
