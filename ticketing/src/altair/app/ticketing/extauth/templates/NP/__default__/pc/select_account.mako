<%inherit file="base.mako" />
<h1>会員資格をご選択ください</h1>
<ul>
%for membership in memberships:
  <li>
    <a href="${_context.route_path('extauth.authorize', _query=dict(_=request.session.get_csrf_token(), member_kind_name=membership['kind']['name'], membership_id=membership['membership_id']))}" class="btn">
      <span class="membership--kind">${membership['kind']['name']}</span>
      % if not membership_ids_are_the_same:
      <span class="membership--membership_id">会員番号: ${membership['displayed_membership_id']}</span>
      % endif
    </a>
  </li>
%endfor
</ul>

