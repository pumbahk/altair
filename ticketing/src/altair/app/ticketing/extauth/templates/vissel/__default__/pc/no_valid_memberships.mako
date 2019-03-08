<%inherit file="base.mako" />

<section class="main none">
<div class="wrap">
<p class="lead">${_(u'ご入力いただいた楽天IDはファンクラブ会員IDと連携していない楽天IDです。')}<br>${_(u'一般（非ファンクラブ会員）の方は「次へ進む」からお進みください。')}</p>
<div class="boxArea clearfix">
<!-- member loginbox -->
<div class="box login-box">
<dl>
<dt class="login-name"><span>${_(u'一般の方')}</span></dt>
<dd class="login-inbox">
<a href="${_context.route_path('extauth.authorize', _query=dict(_=request.session.get_csrf_token(), use_fanclub=False))}">
<p><button class="btnA">${_(u'次へ進む')}</button></p>
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
<dt class="login-name"><span>${_(u'ファンクラブに入会済み')}</span></dt>
<dd class="login-inbox">
<p><a href="https://vissel.fanclub.rakuten.co.jp/mypage/login" class="btnA">${_(u'楽天ID連携をする')}</a></p>
</dd>
</dl>
</div>
<div class="box clearfix">
<p style="text-align:center">
${_(u'※ファンクラブに入会をご希望の方は{}こちら{}から').format('<a href="https://vissel.fanclub.rakuten.co.jp/">', '</a>')|n}
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
