<%inherit file="base.mako" />

<section class="main none">
<div class="wrap">
<p class="lead">ご入力いただいた楽天会員IDはファンクラブ会員IDと連携していない楽天会員IDです。<br>一般（非ファンクラブ会員）の方は「次へ進む」からお進みください。</p>
<div class="boxArea clearfix">
<!-- member loginbox -->
<div class="box login-box">
<dl>
<dt class="login-name"><span>一般の方</span></dt>
<dd class="login-inbox">
<a href="${_context.route_path('extauth.authorize', _query=dict(_=request.session.get_csrf_token(), use_fanclub=False))}">
<p><button class="btnA">次へ進む</button></p>
</a>
</dd>
</dl>
</div>

<!-- FC loginbox -->
<%!
from datetime import datetime
thisyear = datetime.now().strftime('%Y')
%>
<div class="box login-box">
<dl>
<dt class="login-name"><span>ファンクラブに入会済み</span></dt>
<dd class="login-inbox">
<p><a href="https://vissel.fanclub.rakuten.co.jp/mypage/login/ridLogin?year=${thisyear}" class="btnA">楽天ID連携をする</a></p>
</dd>
</dl>
</div>
<div class="box clearfix">
<p style="text-align:center">
※ファンクラブに入会をご希望の方は<a href="">こちら</a>から
</p>
</div>
</div><!-- /boxArea -->
</div><!-- /wrap -->
<!-- back to top--><div id="topButton"><a>▲<br>上へ</a></div><!-- /back to top-->
</section><!-- /main -->

<!--SiteCatalyst-->
<%
    sc = {"pagename": "error-not-valid-user"}
%>
<%include file="../common/sc_basic.html" args="sc=sc" />
<!--/SiteCatalyst-->
