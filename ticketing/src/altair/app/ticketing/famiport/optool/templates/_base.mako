<!DOCTYPE html>
<html lang="ja">
<head>
    <title>運用ツール - <%block name="title"></%block></title>
    <meta name="apple-mobile-web-app-capable" content="yes" />
    <meta name="viewport" content="width=device-width, maximum-scale=1.0, minimum-scale=1.0" />
    <meta charset="UTF-8" />
    <link href="${request.static_url('altair.app.ticketing.famiport.optool:static/css/bootstrap.min.css')}" rel="stylesheet">
    <link href="${request.static_url('altair.app.ticketing.famiport.optool:static/css/main.css')}" rel="stylesheet"/>
    <script src="${request.static_url('altair.app.ticketing.famiport.optool:static/js/jquery-1.11.3.min.js')}"></script>
    <script src="${request.static_url('altair.app.ticketing.famiport.optool:static/js/bootstrap.min.js')}"></script>
    <%block name="head_extras"></%block>
</head>
<body>
  <div class="container">
      <!-- header global navigation -->
      % if request.authenticated_userid:
        <%include file="/_navigation.mako" />
      % endif
      <% flash = request.session.pop_flash() %>
      % if flash:
      <div>
          <ul class="list-group">
            % for message in flash:
            <li class="list-group-item list-group-item-warning">${message}</li>
            % endfor
          </ul>
      </div>
      % endif

      <div>
        ${next.body()}
      </div>
      <footer style="text-align:center;">
          <%block name="footer_extras"></%block>
          <div>&copy; TicketStar Inc.</div>
          <div>version =</div>
      </footer>
  </div>
</body>
</html>
