<!DOCTYPE html>
<html lang="en">
<head>
    <title>運用ツール - <%block name="title"></%block></title>
    <meta name="apple-mobile-web-app-capable" content="yes" />
    <meta name="viewport" content="width=device-width, maximum-scale=1.0, minimum-scale=1.0" />
    <meta charset="UTF-8" />
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" type="text/css" href="${request.static_url('altair.app.ticketing.famiport.optool:static/css/main.css')}" />
</head>
<body>
  % if request.authenticated_userid:
  <%include file="/_navigation.mako" />
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
