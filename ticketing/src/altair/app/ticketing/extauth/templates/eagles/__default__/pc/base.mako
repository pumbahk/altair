<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,minimum-scale=1.0,maximum-scale=1.0,user-scalable=no">
<title>イーグルスチケット ログイン</title>
<link rel="shortcut icon" href="${view_context.static_url('images/eagles.ico')}" />
<link rel="stylesheet" type="text/css" href="${view_context.static_url('css/mypage.css')}" media="all">
<link rel="stylesheet" type="text/css" href="${view_context.static_url('css/toggle.css')}" media="all">
<script type="text/javascript" src="${view_context.static_url('js/jquery.min.js')}"></script>
<script type="text/javascript" src="${view_context.static_url('js/jquery.tile.js')}"></script>
<script>
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
<script src="http://html5shiv.googlecode.com/svn/trunk/html5.js" type="text/javascript"></script>
<![endif]-->
<!--[if lt IE 9]>
<script src="http://css3-mediaqueries-js.googlecode.com/svn/trunk/css3-mediaqueries.js"></script>
<![endif]-->
</head>
<body class="login">

<div class="wrapper">
<!-- ========== HEADER [start] ========== -->
<header class="content_l header">
<div class="content_m">
<h1 class="header-logo"><a href="http://eagles.tstar.jp/"><img src="${view_context.static_url('images/eticket_logo.png')}" alt="イーグルスチケット"></a></h1>
% if request.authenticated_userid and hasattr(_context, 'route_path'):
<p class="logout-btnbox"><a href="${_context.route_path('extauth.logout')}" class="logoutBtn">ログアウト</a></p>
% endif
</div>
<nav class="content_l nav-global">
<div id="toggle"><a href="#">&nbsp;</a></div>
<ul class="content_m clearfix">
<li><a href="http://eagles.tstar.jp/">TOP</a></li>
</ul>
</nav>
</header>
<!-- ========== HEADER [end] ========== -->
<!-- ========== CONTENTS [start] ========== -->
<section class="content_l main">
<div class="content_m radius_l">
${self.body()}
</div>
</section>
<!-- ========== CONTENTS [end] ========== -->
<!-- ========== FOOTER [start] ========== -->
<footer class="content_l footer">
<div class="content_m">
<nav class="nav-footer">
<ul class="clearfix">
<li><a href="http://www.ticketstar.jp/corporate/" target="_blank">運営会社</a></li>
<li><a href="https://f.msgs.jp/webapp/hear/org/showEnquete.do?enqueteid=3&amp;clientid=13074&amp;databaseid=wit" target="_blank">お問い合わせ</a></li>
<li><a href="http://privacy.rakuten.co.jp/" target="_blank">個人情報保護方針</a></li>
<li><a href="http://eagles.tstar.jp/legal" target="_blank">特定商取引法に基づく表示</a></li>
</ul>
</nav>
<p class="copyright clear">&copy; TicketStar Inc.</p>
</div>
</footer>
<!-- ========== FOOTER [end] ========== -->
</div>
</body>
</html>
