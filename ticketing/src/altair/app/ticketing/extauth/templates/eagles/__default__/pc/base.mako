<!doctype html>
<html lang="ja" class="no-js">
<head>
  <title>ログイン | イーグルスチケット（Eチケ）</title>
  <meta charset="utf-8">
<meta http-equiv="x-ua-compatible" content="ie=edge">
<script type="text/javascript">
if ((navigator.userAgent.indexOf('iPhone') > 0) || navigator.userAgent.indexOf('iPod') > 0 || navigator.userAgent.indexOf('Android') > 0) {
        document.write('<meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">');
    }else{
        document.write('<meta name="viewport" content="width=1040, user-scalable=yes">');
    }
</script>
<meta name="description" content="プロ野球 東北楽天ゴールデンイーグルスのオフィシャルチケットサイト。チケット購入は『イーグルスチケット（Eチケ）』で！
">
<meta name="keywords" content="Eチケ,イーチケ,イーグルスチケット,EAGLES TICKET,eagles ticket,楽天イーグルス,RAKUTEN EAGLES,rakuten eagles,イーグルス,EAGLES,rakuten,楽天イーグルス チケット,RAKUTEN EAGLES TICKET,rakuten eagles ticket">

<script src="https://use.typekit.net/etv4epw.js"></script>
<script>try{Typekit.load({ async: true });}catch(e){}</script>

<link rel="shortcut icon" type="image/vnd.microsoft.icon" href="${view_context.static_url('images/eagles.ico')}">
<link rel="apple-touch-icon" sizes="180x180" href="${view_context.static_url('images/touch.png')}">
<link rel="apple-touch-icon-precomposed" href="${view_context.static_url('images/touch.png')}">
<link rel="shortcut icon" href="${view_context.static_url('images/touch.png')}">
<link rel="icon" sizes="192x192" href="${view_context.static_url('images/touch.png')}">
<link rel="stylesheet" href="${view_context.static_url('css/common.css')}">
<link rel="stylesheet" href="${view_context.static_url('css/login.css')}">
<script src="${view_context.static_url('js/libs/modernizr-custom.js')}"></script>
</head>

<body>
<div id="fb-root"></div>
<div class="page">
    <header>
  <div class="inner">
    <h1 class="title"><a href="/"><img src="${view_context.static_url('images/logo.png')}" alt="イーグルスチケット"></a></h1>
  </div>
% if request.authenticated_userid and hasattr(_context, 'route_path'):
  <div class="g-nav-box">
    <nav class="g-nav-list">
      <ul>
        <li>
        <li class="pc">
          <a href="${_context.route_path('extauth.logout')}">ログアウト</a>
        </li>
      </ul>
    </nav>
    <!-- /.g_nav -->
  </div>
  <a href="${_context.route_path('extauth.logout')}" class="buy-link sp">ログアウト</a>
% endif
  <div class="hbg" id="showBtn">
    <button>
      <span></span>
    </button>
    <nav class="humberger-menu-wrap">
      <div class="hbg-inner">
        <h1 class="hum-logo sp"><a href="/"><img src="${view_context.static_url('images/logo.png')}" alt="イーグルスチケット" title="イーグルスチケット"></a></h1>
        <ul class="humberger-menu-list-box">
          <li class="parent-menu humberger-menu-list">
            <h2 class="humberger-menu-ttl js-has-sub-menu">ご利用ガイド<span></span></h2>
            <ul class="sub-menu">
              <li><a href="/help">チケット購入方法</a></li>
              <li><a href="/payment">支払・受取方法</a></li>
              <li><a href="/faq">よくある質問</a></li>
              <li><a href="/caution">ご購入前の注意</a></li>
            </ul>
          </li>
          <li class="parent-menu humberger-menu-list">
              <h2 class="humberger-menu-ttl js-has-sub-menu">サイトについて<span></span></h2>
              <ul class="sub-menu">
                <li><a href="//privacy.rakuten.co.jp/" class="ex-link" target="_blank">個人情報保護方針<img src="${view_context.static_url('images/icon-link-white.png')}" alt="リンク"></a></li>
                <li><a href="/legal">特定商取引に基づく表示</a></li>
                <li><a href="/agreement">サービス利用規約</a></li>
                <li><a href="https://form.rakuteneagles.jp/einfo" target="_blank" class="ex-link">お問い合わせ<img src="${view_context.static_url('images/icon-link-white.png')}" alt="リンク"></a></li>
              </ul>
          </li>
          <li class="parent-menu humberger-menu-list">
            <h2 class="humberger-menu-ttl js-has-sub-menu">チケット購入<span></span></h2>
            <ul class="sub-menu">
              <li><a href="/help">購入方法</a></li>
              <li><a href="/orderreview">購入履歴の確認</a></li>
              <li><a href="/price">チケット価格について</a></li>

            </ul>
          </li>
          <li class="humberger-menu-list"><a href="//www.rakuteneagles.jp/stadium/access/" target="_blank" class="ex-link">アクセス<img src="${view_context.static_url('images/icon-link-white.png')}" alt="リンク"></a></li>
          <li class="humberger-menu-list"><a href="//www.tenki.jp/leisure/baseball/2/7/31015.html" target="_blank" class="ex-link">天気予報<img src="${view_context.static_url('images/icon-link-white.png')}" alt="リンク"></a></li>
        </ul>
      </div>
    </nav>
  </div>

</header>

${self.body()}

<footer>
  <div class="page-top-box">
    <a href="#" class="sp page-top" id="pageTop">
      <span class="arrow top"></span>
    </a>
  </div>

  <p class="copyright">
    <small>&copy; TicketStar, Inc.</small>
  </p>
</footer>  </div>
  <!-- /.page -->
  <script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js"></script>
<script> (window.jQuery || document .write('<script src="${view_context.static_url('js/jquery.js')}"><\/script>')); </script>
<script src="${view_context.static_url('js/app.js')}"></script>
<script src="${view_context.static_url('js/common.js')}"></script>
</body>
</html>
