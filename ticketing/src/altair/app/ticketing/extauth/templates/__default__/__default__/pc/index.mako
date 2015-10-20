<%inherit file="base.mako" />
<ul>
  <li><p><a href="${_context.route_path('extauth.rakuten.entry')}">楽天会員としてログイン</a></p></li>
  % for member_set in _context.member_sets:
  <li>
    <%
    _username = _password = _message = u''
    if member_set == selected_member_set:
      _username = username
      _password = password
      _message = message
    %> 
    <p>${member_set.display_name}ログイン</p>
    <p>会員種別: ${u' / '.join(member_kind.name for member_kind in member_set.member_kinds if member_kind.show_in_landing_page)}</p>
    <form action="${_context.route_path('extauth.login')}" method="POST">
      <p>
      % for member_kind in member_set.member_kinds:
      % if member_kind.show_in_landing_page and member_kind.enable_guests:
      <input type="submit" name="doGuestLoginAs${member_kind.name}" value="${member_kind.display_name}としてゲストログイン" />
      % endif
      % endfor
      </p>
    </form>
    <form action="${_context.route_path('extauth.login')}" method="POST">
      % if _message:
      <p>${_message}</p>
      % endif
      <label for="stockholder-username">ユーザ名</label>
      <input id="stockholder-username" type="text" name="username" value="${_username}" />
      % if member_set.use_password:
      <label for="stockholder-password">パスワード</label>
      <input id="stockholder-password" type="password" name="password" value="${_password}" />
      % endif
      <input type="hidden" name="member_set" value="${member_set.name}" />
      <input type="hidden" name="_" value="${request.session.get_csrf_token()}" />
      <input type="submit" value="ログイン" />
    </form>
  </li>
  % endfor
</ul>
