<%inherit file="base.mako" />

<p class="box bold tac fs18" style="color: red;">ご入力いただいた楽天会員IDはファンクラブ会員IDと連携していない楽天会員IDです。<br>一般（非ファンクラブ会員）の方は「次へ進む」からお進みください。</p>

<div class="box clearfix">

<!-- guest LOGIN BOX -->
<div class="col2 tile2 login-box">
<dl>
<dt class="login-name"><span>一般の方</span></dt>
<dd class="login-inbox">
% for membership in memberships:
<a href="${_context.route_path('extauth.authorize', _query=dict(_=request.session.get_csrf_token(), member_kind_id=membership['kind']['id'], membership_id=membership['membership_id']))}">
<p class="mgt20 mgb20"><button class="btnA btnA_l">次へ進む</button></p>
</a>
% endfor
</dd>
</dl>
</div>

<!-- FC LOGIN BOX -->
<div class="col2 tile2 login-box">
<dl>
<dt class="login-name"><span>ファンクラブに入会済み</span></dt>
<dd class="login-inbox">
<%!
from datetime import datetime
thisyear = datetime.now().strftime('%Y')
%>
<p class="mgt20 mgb20"><a href="https://eagles.fanclub.rakuten.co.jp/mypage/login/ridLogin?year=${thisyear}" class="btnA btnA_l">楽天ID連携をする</a></p>
</dd>
</dl>
</div>

<div class="box clearfix">
<p style="text-align:center">
※ファンクラブに入会をご希望の方は<a href="http://www.rakuteneagles.jp/fanclub/">こちら</a>から
</p>
</div>

<!--SiteCatalyst-->
<%
    sc = {"pagename": "error-not-valid-user"}
%>
<%include file="../common/sc_basic.html" args="sc=sc" />
<!--/SiteCatalyst-->

