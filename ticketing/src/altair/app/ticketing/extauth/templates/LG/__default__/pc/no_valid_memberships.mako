<%inherit file="base.mako" />
<h1>有効な会員との紐付がありません</h1>

% for membership in memberships:
<a href="${_context.route_path('extauth.authorize', _query=dict(_=request.session.get_csrf_token(), member_kind_id=membership['kind']['id'], membership_id=membership['membership_id']))}">
<p class="mgt20 mgb20"><button class="btnA btnA_l">次へ進む</button></p>
</a>
% endfor
