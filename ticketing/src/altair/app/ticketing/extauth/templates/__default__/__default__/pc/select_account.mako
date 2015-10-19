<%inherit file="base.mako" />
<p>${last_name} ${first_name}さんこんにちは。</p>

<ul>
%for membership in memberships:
  <li>
    <a href="${request.route_path('extauth.authorize', subtype=_context.subtype, _query=dict(member_kind_id=membership['kind']['id'], membership_id=membership['membership_id']))}" class="btn">
      <span class="membership--kind">${membership['kind']['name']}</span>
      <span class="membership--membership_id">会員番号: ${membership['membership_id']}</span>
    </a>
  </li>
%endfor
</ul>
