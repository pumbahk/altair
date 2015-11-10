<%inherit file="base.mako" />
<div class="statusBox">

<p class="statusText">購入するファンクラブ会員ステータスを選択してください</p>

<ul class="statusList clearfix">
%for membership in memberships:
<li class="${membership['kind']['aux']['style_class_name']}">
<a href="${_context.route_path('extauth.authorize', _query=dict(_=request.session.get_csrf_token(), member_kind_id=membership['kind']['id'], membership_id=membership['membership_id']))}">
  <span class="member_kind">${membership['kind']['name']}</span>
  <span class="member_id tac">会員ID：${membership['displayed_membership_id']}</span>
</a>
</li>
%endfor
</ul>
</div>

