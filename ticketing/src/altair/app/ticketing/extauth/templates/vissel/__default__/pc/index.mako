<%inherit file="base.mako" />
<% member_set = _context.member_sets[0] %>
<section class="main login">
<div class="wrap">
<p class="lead">ヴィッセル神戸公式チケットサイトでのチケットのお求めには楽天会員IDが必要になりました。<br>楽天会員IDをお持ちでないお客様は会員登録をお願いします。</p>
<div class="boxArea clearfix">
<!-- member loginbox -->
<div class="box login-box">
<dl>
<dt class="login-name" id="rakulogintitle"><span>ファンクラブ会員の方</span></dt>
<dd class="login-inbox" id="rakulogin">
<p><a href="${_context.route_path('extauth.rakuten.entry')}" class="btnA"><span class="login-fc-btn">楽天会員IDでログイン</span></a></p>
<%!
from datetime import datetime
thisyear = datetime.now().strftime('%Y')
%>
<p><a href="https://vissel.fanclub.rakuten.co.jp/mypage/login/ridLogin?year=${thisyear}" class="btnID" target="_blank">楽天会員ID連携がお済でない方はこちら</a></p>
<div class="textArea">
<p class="caution">※ファンクラブ会員と連携した楽天会員ID・パスワードが必要です。</p>
<p class="column">※楽天会員ID・パスワードを忘れてしまった方は<a href="https://member.id.rakuten.co.jp/rms/nid/upkfwd" target="_blank">こちら</a></p>
</div>
<!-- stockholder LOGIN BOX -->
<div class="btn-stockholder">
<p class="clear tar">&raquo; <a href="${_context.route_path('extauth.login', _query=dict(member_set=member_set.name))}"><span>その他会員の方はこちらから</span></a></p>
</div>
</dd>
</dl>
</div>
<!-- guest loginbox -->
<div class="box login-box">
<dl>
<dt class="login-name" id="guestlogintitle"><span>一般の方</span></dt>
<dd class="login-inbox" id="guestlogin">
<p class="rakuten-login-button"><a href="${_context.route_path('extauth.rakuten.entry', _query=dict(use_fanclub=False))}" class="btnA btnA_l"><span class="login-fc-btn">楽天会員IDでログイン</span></a></p>
<p><a href="" class="btnID" target="_blank">楽天会員に新規登録(無料)してサービスを利用する</a></p>
</dd>
</dl>
</div>
</div><!-- /boxArea -->

<article>
<div class="login_adBox">
<p>座席選択を快適にご利用していただくために、以下のブラウザでのご利用を推奨します。</p>
<dl>
<dt>Windows</dt>
<dd>Google Chrome</dd>
<dd>Mozilla Firefox 13.0以降</dd>
<dd>Internet Explorer 9.x以降</dd>
<dt>Mac</dt>
<dd>Safari 5.0以降</dd>
</dl>
<div class="login_adInner">
<p>
※Internet Explorer 8.x, 7.x, 6.x をお使いの方は、座席を選んでの購入が出来ません。「おまかせ」のみの購入となります。
座席選択対応ブラウザは下記よりダウンロードしてください。</p>
<ul>
<li><a href="//www.google.com/intl/ja/chrome/browser/">Google Chrome</a></li>
<li><a href="//www.mozilla.jp/firefox/">Mozilla Firefox</a></li>
</ul>
</div><!-- /login_adInner -->
</div><!-- /login_adBox -->
</article>
</div><!-- /wrap -->
<!-- back to top--><div id="topButton"><a>▲<br>上へ</a></div><!-- /back to top-->
</section><!-- /main -->

<!--SiteCatalyst-->
<%
    sc = {"pagename": "extauth-index"}
%>
<%include file="../common/sc_basic.html" args="sc=sc" />
<!--/SiteCatalyst-->
