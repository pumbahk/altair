<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,minimum-scale=1.0,maximum-scale=1.0,user-scalable=no">
<title>ログイン | レジャーチケット | </title>
<link rel="shortcut icon" href="${view_context.static_url('img/common/favicon.ico')}">
<link rel="stylesheet" href="${view_context.static_url('css/grpRakutenCommon.css')}" type="text/css" media="all">
<link rel="stylesheet" href="${view_context.static_url('css/login.css')}" type="text/css" media="all">
<script type="text/javascript" src="${view_context.static_url('js/jquery.js')}"></script>
<script type="text/javascript" src="${view_context.static_url('js/jquery.tile.js')}"></script>
<script type="text/javascript" src="${view_context.static_url('js/toggle.js')}"></script>
<!--[if lt IE 9]>
<script src="//html5shiv.googlecode.com/svn/trunk/html5.js" type="text/javascript"></script>
<![endif]-->
<!--[if lt IE 9]>
<script src="//css3-mediaqueries-js.googlecode.com/svn/trunk/css3-mediaqueries.js"></script>
<![endif]-->
</head>

<body>
<header class="header"><!-- headder -->
<!-- ******************** header [start] ******************** -->
<div id="grpHeader">
<!-- ===== grpH-utility [start] ===== -->
<div class="grpH-utility clearfix">
<div class="grpH-inner">
<ul class="grpH-group-nav">
<!-- <li id="grpNote"><noscript><a href="https://card.rakuten.co.jp/entry/">今すぐ2,000ポイント！</a></noscript></li> -->
<li class="grpH-dropdown grpH-group-dropdown"><a href="http://www.rakuten.co.jp/sitemap/">楽天グループ<i class="grpH-icon-arrow"></i></a>
<ul class="grpH-dropdown-panel">
<li><a href="//video.rakuten.co.jp/" rel="nofollow">ショウタイム</a></li>
<li><a href="//entertainment.rakuten.co.jp/" rel="nofollow">エンタメナビ</a></li>
<li><a href="//www.rakuten.co.jp/sitemap/">サービス一覧</a></li>
</ul>
</li>
<li><a href="//books.rakuten.co.jp/" rel="nofollow">ブックス</a></li>
<li><a href="//travel.rakuten.co.jp/" rel="nofollow">トラベル</a></li>
<li><a href="//www.rakuten.co.jp/">楽天市場</a></li>
</ul>
</div></div><!-- ===== grpH-utility [end] ===== -->

<div id="tsHeader">
<!-- ===== grpH-service [start] ===== -->
<div class="grpH-service clearfix">
<div class="grpH-site-id clearfix">
<div class="grpH-logo"><h1><a href="/"><span class="offleft">レジャーチケット</span></a></h1>
</div>
</div>

<div class="grpH-site-menu clearfix">
<div class="grpH-menu-btns">
<ul class="grpH-help-nav">
<li class="first"><a href="/howto">購入の流れ</a></li>
<li><a href="/faq">よくある質問</a></li>
<li><a href="http://emagazine.rakuten.co.jp/#17">メルマガを購読する</a></li>
% if hasattr(_context, 'subtype') and request.authenticated_userid:
<li><a href="${request.route_path('extauth.logout', subtype=_context.subtype)}">ログアウトする</a></li>
% endif
</ul>
</div>
</div>
</div><!-- ===== grpH-service [end] ===== -->
</div><!-- /tsHeader-->
</div><!-- /grpHeader-->
<!-- menu -->
<nav class="nav-global">
<div id="toggle"><a href="#">&nbsp;</a></div>
<ul class="clearfix">
<li class="first"><a href="/howto">購入の流れ</a></li>
<li><a href="/faq">よくある質問</a></li>
<li><a href="http://emagazine.rakuten.co.jp/#17">メルマガを購読する</a></li>
</ul>
</nav>
<!-- /menu -->
</header><!-- /header -->

${self.body()}

<footer class="footer">
<div id="grpFooter">
<!-- ========== grpFooter ========== -->
<!-- Standard RakutenCommonHeader v0.1.4 CSS starts-->
<link rel="stylesheet" href="${view_context.static_url('css/rc-f-standard.css')}" type="text/css" media="all" />
<!-- Standard RakutenCommonHeader v0.1.4 CSS ends-->
<div class="rc-f-standard rc-f-fixed rc-f-custom00">
<div class="rc-f-section-content00">
<div class="rc-f-section-bar rc-f-first">
<div class="rc-f-inner">
<dl class="rc-f-dl-inline-box">
<dt class="rc-f-dl-title01 rc-f-text-em">楽天グループ</dt>
<dd>
<ul class="rc-f-list-inline">
<li><a href="//www.rakuten.co.jp/sitemap/" class="rc-f-btn"><span>サービス一覧</span></a></li><li><a href="//www.rakuten.co.jp/sitemap/inquiry.html" class="rc-f-btn"><span>お問い合わせ一覧</span></a></li>
</ul>
</dd>
</dl>
</div>
</div>
<div class="rc-f-section-bar">
<div class="rc-f-inner">
<dl class="rc-f-dl-inline rc-f-block">
<dt class="rc-f-dl-title01">おすすめ</dt>
<dd class="rc-f-text-strong" id="grpRakutenRecommend"></dd>
</dl>
<ul class="rc-f-row rc-f-row-dot rc-f-row4">
<li class="rc-f-col rc-f-first">
<div class="rc-f-media rc-f-nav-item">
<div class="rc-f-media-head"><a href="//entertainment.rakuten.co.jp/">旬なエンタメ情報を見る</a></div>
<div class="rc-f-media-body">楽天エンタメナビ</div>
</div>
</li>
<li class="rc-f-col">
<div class="rc-f-media rc-f-nav-item rc-f-nav-item-delimit">
<div class="rc-f-media-head"><a href="//video.rakuten.co.jp/">映画・ドラマ・アニメ動画もっと見る</a></div>
<div class="rc-f-media-body">楽天SHOWTIME</div>
</div>
</li>
<li class="rc-f-col">
<div class="rc-f-media rc-f-nav-item rc-f-nav-item-delimit">
<div class="rc-f-media-head"><a href="//books.rakuten.co.jp/">本・CD・DVDを購入する</a></div>
<div class="rc-f-media-body">楽天ブックス</div>
</div>
</li>
<li class="rc-f-col">
<div class="rc-f-media rc-f-nav-item rc-f-nav-item-delimit">
<div class="rc-f-media-head"><a href="//www.rakuten-card.co.jp/">ポイント2倍のカードを申込む</a></div>
<div class="rc-f-media-body">楽天カード</div>
</div>
</li>
</ul>
</div>
</div><!-- /.rc-f-section-bar -->
</div><!-- /.rc-f-section-content00 -->
</div><!-- /.rc-f-standard -->
<script type="text/javascript" src="//jp.rakuten-static.com/1/js/grp/ftr/js/parm_selector_footer.js"></script>
<!-- ========== /grpFooter ========== -->
<div id="grpRakutenLinkArea">
<div id="companyFooter">
<ul>
<li><a href="//www.ticketstar.jp/">運営会社</a></li>
<li><a href="mailto:leisure@tstar.jp">お問い合わせ</a></li>
<li><a href="//www.ticketstar.jp/privacy">個人情報保護方針</a></li>
<li><a href="//www.ticketstar.jp/legal">特定商取引法に基づく表示</a></li>
</ul>
<p id="copyright">&copy; TicketStar, Inc.</p>
</div><!-- /div#companyFooter -->
</div><!-- /div#grpFooter -->

</div><!-- /.rc-f-standard -->
</footer><!-- /footer -->
</body>
</html>
