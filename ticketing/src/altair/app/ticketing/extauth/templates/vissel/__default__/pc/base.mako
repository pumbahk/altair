<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0,minimum-scale=1.0,maximum-scale=1.0,user-scalable=no">
  <title>${_(u'ヴィッセル神戸')} ${_(u'公式チケットサイト')} ${_(u'ログイン')}</title>
  <link rel="shortcut icon" href="${view_context.static_url('images/favicon.ico')}">
  <link rel="stylesheet" type="text/css" href="${view_context.static_url('css/common.css')}" media="all"/>
  <link rel="stylesheet" type="text/css" href="${view_context.static_url('css/toggle.css')}" media="all"/>
  <script type="text/javascript" src="${view_context.static_url('js/jquery-1.7.2.min.js')}"></script>
  <script type="text/javascript" src="${view_context.static_url('js/scroll.js')}"></script>
  <script>
    $(function () {
      $("#toggle").click(function () {
        $(".nav-global ul").slideToggle();
        return false;
      });
      $(window).resize(function () {
        var win = $(window).width();
        var p = 480;
        if (win > p) {
          $(".nav-global ul").show();
        } else {
          $(".nav-global ul").hide();
        }
      });
      $("#rakulogintitle").click(function () {
        $("#rakulogin").show();
        return false;
      });
      $("#guestlogintitle").click(function () {
        $("#guestlogin").show();
        return false;
      });
      $("#annuallogintitle").click(function () {
        $("#annuallogin").show();
        return false;
      });
      $("#otherlogintitle").click(function () {
        $("#otherlogin").show();
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
    <h1 class="header-logo"><a href="//vissel.tstar.jp/"><img src="${view_context.static_url('images/ticket_logo.png')}" alt="ヴィッセルチケット"></a></h1>
    <!-- menu -->
    <nav class="nav-global">
      <div id="toggle"><a href="https://vissel.tstar.jp/orderreview/#">&nbsp;</a></div>
      <ul class="clearfix">
        <li><a href="https://vissel.tstar.jp/">TOP</a></li>
      </ul>
    </nav>
    <!-- /menu -->
  </div>
</header>
<!-- /headder -->

${self.body()}

<!-- footer -->
<footer>
  <div class="wrap clearfix">
    <div class="box">
      <p class="footer-logo">
        <img src="${view_context.static_url('images/slogun.png')}" alt="ヴィッセル"/>
      </p>
    </div>
    <div class="box">
      <nav class="nav-footer">
        <ul class="clearfix">
          <li><a href="//www.ticketstar.jp/corporate/" target="_blank">${_(u'運営会社')}</a></li>
          <li><a href="//vissel.tstar.jp/agreement" target="_blank">${_(u'利用規約')}</a></li>
          <li><a href="mailto:vissel@tstar.jp" target="_blank">${_(u'お問い合わせ')}</a></li>
          <li><a href="//www.ticketstar.jp/privacy/" target="_blank">${_(u'個人情報保護方針')}</a></li>
          <li><a href="//vissel.tstar.jp/cancel" target="_blank">${_(u'キャンセルポリシー')}</a></li>
          <li><a href="//vissel.tstar.jp/legal" target="_blank">${_(u'特定商取引法に基づく表示')}</a></li>
        </ul>
      </nav>
      <p class="copyright">© TicketStar Inc. All Rights Reserved.</p>
    </div>
  </div>
</footer>
<!-- /footer -->
</body>
</html>
