<context.static_url('!DOCTYPE html')>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,minimum-scale=1.0,maximum-scale=1.0,user-scalable=no">
<title>ヴィッセル神戸公式チケットサイト ログイン</title>
<link rel="shortcut icon" href="${view_context.static_url('images/favicon.ico')}">
<link rel="stylesheet" type="text/css" href="${view_context.static_url('css/common.css')}" media="all" />
<link rel="stylesheet" type="text/css" href="${view_context.static_url('css/toggle.css')}" media="all" />
<script type="text/javascript" src="${view_context.static_url('js/jquery-1.7.2.min.js')}"></script>
<script type="text/javascript" src="${view_context.static_url('js/scroll.js')}"></script>
<script>
$(function(){
  $("#toggle").click(function(){
    $(".nav-global ul").slideToggle();
    return false;
  });
  $(window).resize(function(){
    var win = $(window).width();
    var p = 480;
    if(win > p){
      $(".nav-global ul").show();
    } else {
      $(".nav-global ul").hide();
    }
  });
  $("#rakulogintitle").click(function(){
      $("#rakulogin").show();
    return false;
  });
  $("#guestlogintitle").click(function(){
      $("#guestlogin").show();
    return false;
  });
});
</script>
<!--[if lt IE 9]>
<script src="//html5shiv.googlecode.com/svn/trunk/html5.js" type="text/javascript"></script>
<![endif]-->
<!--[if lt IE 9]>
<script src="//css3-mediaqueries-js.googlecode.com/svn/trunk/css3-mediaqueries.js"></script>
<![endif]-->
</head>
<body>

<!-- headder -->
<header class="header">
<div class="wrap">
<h1 class="header-logo"><a href="/"><img src="${view_context.static_url('images/logo.gif')}" alt="ヴィッセルチケット"></a></h1>
% if request.authenticated_userid and hasattr(_context, 'route_path'):
<p class="logout-btnbox"><a href="${_context.route_path('extauth.logout')}" class="logoutBtn">ログアウト</a></p>
% endif
<!-- /menu -->
</div><!-- /wrap -->
</header><!-- /headder -->

${self.body()}

<!-- footer -->
<footer class="footer">
<div class="wrap clearfix">
<div class="box">
<p class="for-sp-img">
<img src="//tstar.s3.amazonaws.com/asset/vissel/2014-03-06/c887e7171e7342d2916ffb7b08f4501e.png" alt="ヴィッセル"/></p>
</div>
<div class="box">
<!-- menu -->
<nav class="nav-footer">
<ul class="clearfix">
<li><a href="//www.ticketstar.jp/corporate/" target="_blank">運営会社</a></li>
<li><a href="//vissel.tstar.jp/agreement" target="_blank">利用規約</a></li>
<li><a href="mailto:vissel@tstar.jp" target="_blank">お問い合わせ</a></li>
<li><a href="//www.ticketstar.jp/privacy/" target="_blank">個人情報保護方針</a></li>
<li><a href="//vissel.tstar.jp/cancel" target="_blank">キャンセルポリシー</a></li>
<li><a href="//vissel.tstar.jp/legal" target="_blank">特定商取引法に基づく表示</a></li>
</ul>
</nav><!-- /menu -->
<p class="copyright">&copy; TicketStar Inc. All Rights Reserved.</p>
</div>
</div><!-- /wrap -->
</footer><!-- /footer -->
</body></html>
