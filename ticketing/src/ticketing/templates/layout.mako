<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
  <head>
    <title><%block name="title" /> - ALTAIR</title>
    <link href="http://fonts.googleapis.com/css?family=Changa+One" rel="stylesheet" type="text/css">
    <link rel="stylesheet" type="text/css" href="/static/css/flexigrid.css" />
    <link rel="stylesheet" type="text/css" href="/static/css/jquery-ui/smoothness/jquery-ui-1.8.16.custom.css" />
    <link rel="stylesheet" type="text/css" href="/_deform/css/form.css" />
    <link rel="stylesheet" type="text/css" href="/static/css/admin.css" />
    <%block name="more_styles" />
    <script type="text/javascript" src="/static/js/jquery-1.6.2.min.js"></script>
    <script type="text/javascript" src="/static/js/jquery-ui-1.8.16.custom.min.js"></script>
    <script type="text/javascript" src="/_deform/scripts/jquery.form.js"></script>
    <script type="text/javascript" src="/_deform/scripts/jquery.maskedinput-1.2.2.min.js"></script>
    <script type="text/javascript" src="/_deform/scripts/jquery-ui-timepicker-addon.js"></script>
    <script type="text/javascript" src="/static/js/deform.js"></script>
    <script type="text/javascript" src="/static/js/flexigrid.js"></script>
    <script type="text/javascript" src="/static/js/admin.js"></script>
    <%block name="more_scripts" />
  </head>
  <body>
    <div class="page">
      <div class="header">
        <div class="header-content">
          <div class="title">ALTAIR</div>
          <ul class="ui-navbar">
          <%
            menuitems = [
              ['-',                  'admin.top',              u'トップ'],
              ['admin.events',       'admin.events.top',       u'イベント管理'],
              ['admin.users',        'admin.users.top',        u'ユーザ管理'],
              ['admin.purchasables', 'admin.purchasables.top', u'商品管理'],
              ['admin.masterdata',   'admin.masterdata.top',   u'マスタ登録'],
              ]
            menuitems = []
            %>
          % for x in menuitems:
            <li class="ui-navbar-item${ ' selected' if request.matched_route.name.startswith(x[0]) else ''}"><a href="${request.route_path(x[1])}">${x[2]}</a></li>
          % endfor
          </ul>
        </div>
      </div>
      <div class="main">
        <div class="main-content">
          <h1>${self.title()}</h1>
          <%include file="ticketing:templates/_components/breadcrumb.mako" />
          ${next.body(**context.kwargs)}
        </div>
      </div>
      <div class="footer">
        <div class="footer-content">
          2011 Ticketstar, Inc. All Rights Reserved.
        </div>
      </div>
    </div>
  </div>
  <script type="text/javascript">
    applyUIStyles(document);
    deform.load();
  </script>
  </body>
</html>
