<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>運用ツール - <%block name="title"></%block></title>
</head>
<body>
  % if request.authenticated_userid:
  [ログイン中] <a href="${request.route_path('logout')}">ログアウト</a>
  % endif
  <h1>${self.title()}</h1>
  <% flash = request.session.pop_flash() %>
  % if flash:
  <div>
  <ul>
    % for message in flash:
    <li>${message}</li>
    % endfor
  </ul>
  </div>
  % endif

  <div>
    ${next.body()}
  </div>
</body>
</html>
