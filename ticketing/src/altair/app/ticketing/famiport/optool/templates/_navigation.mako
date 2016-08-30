
<nav class="navbar navbar-default">
  <div class="container-fluid">
    <div class="navbar-header">
      <a class="navbar-brand" href="${request.route_url('search.receipt')}"><strong>Famiポート</strong></a>
    </div>
    <div id="navbar" class="navbar-collapse collapse">
      <ul class="nav navbar-nav">
        <li><a href="${request.route_path('search.receipt')}">申込検索</a></li>
        <li><a href="${request.route_path('search.performance')}">公演検索</a></li>
        <li><a href="${request.route_path('search.refund_performance')}">払戻公演データ検索</a></li>
        <li><a href="${request.route_path('search.refund_ticket')}">払戻チケットデータ検索</a></li>
      </ul>
      <ul class="nav navbar-nav navbar-right">
        <li class="active"><a href="${request.route_path('change_password')}">パスワード変更<span class="sr-only">(current)</span></a></li>
        <li class="active"><a href="${request.route_path('logout')}">ログアウト<span class="sr-only">(current)</span></a></li>
      </ul>
    </div>
    <!--/.nav-collapse -->
  </div>
  <!--/.container-fluid -->
</nav>
