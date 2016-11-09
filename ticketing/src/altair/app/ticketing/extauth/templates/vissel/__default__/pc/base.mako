<context.static_url('!DOCTYPE html')>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,minimum-scale=1.0,maximum-scale=1.0,user-scalable=no">
<title>ヴィッセル神戸公式チケットサイト ログイン</title>
<link rel="shortcut icon" href="${view_context.static_url('images/favicon.ico')}">
<link rel="stylesheet" type="text/css" href="${view_context.static_url('css/common.css')}" media="all" />
<link rel="stylesheet" type="text/css" href="${view_context.static_url('css/toggle.css')}" media="all" />
<script type="text/javascript" src="${view_context.static_url('js/jquery-1.7.2.min.js')}"></script>
<script type="text/javascript" src="${view_context.static_url('js/scroll.js')}"></script><script>
$(function(){
  $("#toggle").click(function(){
    $(".nav-global ul").slideToggle();
    return false;
  });
  $("#rakulogintitle").click(function(){
      $("#rakulogin").show();
    return false;
  });
  $("#guestlogintitle").click(function(){
      $("#guestlogin").show();
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
<h1 class="header-logo"><a href="//vissel.tstar.jp/"><img src="${view_context.static_url('images/logo.gif')}" alt="ヴィッセルチケット"></a></h1>
<!-- menu -->
<nav class="nav-global">
<div id="toggle"><a href="#">&nbsp;</a></div>
<ul class="clearfix">
<li><a href="//vissel.tstar.jp/">TOP</a></li>
</ul>
</nav>
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

<!--SiteCatalyst-->
<!--<script type="text/javascript">
var trackingParam = {};
trackingParam.pageName="cart:fc_login"
trackingParam.channel="cart"
</script>//-->

<!-- SiteCatalyst tags -->
<!--<script type="text/javascript" src="//a.ichiba.jp.rakuten-static.com/com/rat/vissel-kobe.co.jp/s_accountSetting.js?v=20160129"></script>
<script type="text/javascript" src="//a.ichiba.jp.rakuten-static.com/com/rat/sc/s_codeCommon.js?v=20160129"></script>
<script type="text/javascript" src="//www.rakuten.co.jp/com/rat/vissel-kobe.co.jp/s_customTracking.js?v=20160129"></script>//-->

<!-- /SiteCatalyst tags -->
<!-- RAT tags -->
<!--<script type="text/javascript" src="//a.ichiba.jp.rakuten-static.com/com/rat/vissel-kobe.co.jp/ral-vissel-kobe.co.jp.js?v=20160129" async defer></script> -->
<!-- /RAT tags -->
<!--/SiteCatalyst-->
<!--<iframe src="//www.rakuten.co.jp/com/rat/plugin/external/ral-iframe-rakuten.co.jp.html?o-id=https%3A%2F%2Fvissel.tstar.jp" style="display: none; visibility: hidden;"></iframe> -->
</body></html>
