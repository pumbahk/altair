<%inherit file="base.mako" />
<%
member_set = _context.member_sets[0]
guest_member_kinds = [member_kind for member_kind in member_set.member_kinds if member_kind.show_in_landing_page and member_kind.enable_guests]
%>

<p class="box bold tac fs18" style="color: red;">有効なファンクラブが確認できません</p>

<div class="box clearfix">

<!-- FC LOGIN BOX -->
<div class="col2_1 tile2 login-box">
<dl>
<dt class="login-name"><span>ファンクラブに入会済み</span>の方はこちら</dt>
<dd class="login-inbox">
<%!
from datetime import datetime
thisyear = datetime.now().strftime('%Y')
%>
<p class="mgt20 mgb20"><a href="https://eagles.fanclub.rakuten.co.jp/mypage/login/ridLogin?year=${thisyear}" class="btnA btnA_l">楽天ID連携をする</a></p>
</dd>
</dl>
</div>

<!-- guest LOGIN BOX -->
% if guest_member_kinds:
<div class="col2_2 tile2 login-box">
<form action="${_context.route_path('extauth.login',_query=request.GET)}" method="POST">
<dl>
<dt class="login-name"><span>一般の方</span>はこちら</dt>
<dd class="login-inbox">
% for member_kind in guest_member_kinds:
<p class="mgt20 mgb20"><button class="btnA btnA_l" name="doGuestLoginAs${member_kind.name}">次へ進む</button></p>
% endfor
</dd>
</dl>
<input type="hidden" name="member_set" value="${member_set.name}" />
<input type="hidden" name="_" value="${request.session.get_csrf_token()}" />
</form>
</div>
% endif

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
