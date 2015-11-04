<%inherit file="base.mako" />
<%
member_set = _context.member_sets[0]
guest_member_kinds = [member_kind for member_kind in member_set.member_kinds if member_kind.show_in_landing_page and member_kind.enable_guests]
%>
<div class="errorBox">

<p class="errorText">ファンクラブ連携が確認できません</p>

<ul class="clearfix">

<li>
<dl>
<dt class="user-guest-name"><span>ファンクラブに入会済み</span>の方はこちら</dt>
<dd>
<p><a href="#${request.authenticated_userid['rakuten']['claimed_id']}" class="btnL">楽天ID連携をする</a></p>
</dd>
</dl>
</li>

% if guest_member_kinds:
<li>
<form action="${_context.route_path('extauth.login')}" method="POST"
<dl>
<dt><span>ファンクラブに未入会</span>の方はこちら</dt>
<dd>
% for member_kind in guest_member_kinds:
<p><button class="btnL" name="doGuestLoginAs${member_kind.name}">ゲスト購入する</a></p>
% endfor
</dd>
</dl>
<input type="hidden" name="member_set" value="${member_set.name}" />
<input type="hidden" name="_" value="${request.session.get_csrf_token()}" />
</form>
</li>
% endif

</ul>
</div>
</div>
