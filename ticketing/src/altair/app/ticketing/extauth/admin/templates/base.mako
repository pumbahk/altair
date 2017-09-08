<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
  <title>ExtAuth admin</title>
  <style type="text/css">
    body {
        padding-top: 60px; /* 60px to make the container go all the way to the bottom of the topbar */
    }
    .navbar-fixed-top {
        position: fixed !important;
        margin: 0 !important;
    }
    .navbar-inner {
        padding: 5px;
    }
    .navbar .nav > li > span {
        padding: 9px 15px;
        font-weight: bold;
        color: #777;
    }
  </style>
</head>
<body>
  <div class="navbar navbar-fixed-top">
    <div class="navbar-inner">
      <div class="container">
        <a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </a>
        <a class="brand" href="${request.route_path('top')}">ExtAuth管理</a>
        <div class="nav-collapse">
          <ul class="nav pull-right">
            % if request.operator is not None:
            <li class="dropdown">
                <a class="dropdown-toggle" data-toggle="dropdown">${request.operator.auth_identifier}<b class="caret"></b></a>
                <ul class="dropdown-menu">
                    <li><a href="${request.route_path('logout')}"><i class="icon-off"></i> ログアウト</a></li>
                </ul>
            </li>
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
