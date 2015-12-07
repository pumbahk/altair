<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
  <title>ExtAuth admin</title>
  <style type="text/css">
body {
  padding-top: 60px; /* 60px to make the container go all the way to the bottom of the topbar */
}

.paid {
  background-color: #ff8;
}

.canceled {
  color: #ddd;
}
</style>
</head>
<body>
  <div class="navbar navbar-fixed-top">
    <div class="navbar-inner">
      <div class="container">
        <a class="brand" href="${request.route_path('top')}">ExtAuth admin</a>
        <div class="nav-collapse">
          <ul class="nav pull-right">
            % if request.operator is not None:
            <li><a href="${request.route_path('logout')}"><i class="icon-off"></i> ログアウト</a></li>
            % endif
          </ul>
        </div><!--/.nav-collapse -->
      </div>
    </div>
  </div>
  <div class="container">
    ${next.body()}
  </div>
</body>
</html>
<!--
vim: sts=2 sw=2 ts=2 et
-->
