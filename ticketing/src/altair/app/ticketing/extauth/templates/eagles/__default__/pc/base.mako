<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
<link rel="shortcut icon" href="${view_context.static_url('images/eagles.ico')}" />
<link rel="stylesheet" type="text/css" href="${view_context.static_url('css/mypage_import2.css')}" media="all" />
<title>イーグルスチケット 会員ログインページ</title>
<script src="${view_context.static_url('js/jquery.min.js')}"></script>
<script type="text/javascript" src="${view_context.static_url('js/jquery.tile.js')}"></script>
</head>
<body>
<div class="header" id="top">
<div class="header-inner">
<h1>
<a href="http://eagles.tstar.jp/">
<img src="${view_context.static_url('images/eticket_logo.png')}" alt="イーグルスチケット" height="70"/>
</a>
</h1>
</div>
</div>

<div class="gnavi">
<ul>
<li><a href="http://eagles.tstar.jp/">TOP</a></li>
</ul>
</div>

<div class="wrapper">
<div class="kadomaru">
${self.body()}
</div>
</div>

<div class="footer">
<div class="footer-inner">
<div class="footernav">
<ul>
<li><a class="first" href="http://www.ticketstar.jp/corporate/" target="_blank">運営会社</a></li>
<li><a href="https://f.msgs.jp/webapp/hear/org/showEnquete.do?enqueteid=3&amp;clientid=13074&amp;databaseid=wit" target="_blank">お問い合わせ</a></li>
<li><a href="http://privacy.rakuten.co.jp/" target="_blank">個人情報保護方針</a></li>
<li><a class="last" href="http://eagles.tstar.jp/legal" target="_blank">特定商取引法に基づく表示</a></li>
</ul>
</div>
<div class="copyright clear">
Copyright © 2010-2015 TicketStar Inc. All Rights Reserved.
</div>
</div>
</div>
</body>
</html>
