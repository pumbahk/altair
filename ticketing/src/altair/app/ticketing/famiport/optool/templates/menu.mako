<!DOCTYPE html>
<html>

<body>
    <!-- Static navbar -->
    <nav class="navbar navbar-default">
      <div class="container-fluid">
        <div class="navbar-header">
          <a class="navbar-brand" href="#"><img src="${request.static_url('altair.app.ticketing.famiport.optool:static/images/famiport_logo.jpg')}" style="width:150px;"/></a>
        </div>
        <div id="navbar" class="navbar-collapse collapse">
          <ul class="nav navbar-nav">
            <li class="active"><a href="#">申込検索</a></li>
            <li><a href="search_per_store.html">店舗別申込検索</a></li>
            <li><a href="search_performance.html">公演検索</a></li>
            <li><a href="search_payback.html">払戻公演データ検索</a></li>
            <li><a href="search_payback_ticket.html">払戻チケットデータ検索</a></li>
          </ul>
          <ul class="nav navbar-nav navbar-right">
            <li class="active"><a href="index.html">logout <span class="sr-only">(current)</span></a></li>
          </ul>
        </div>
        <!--/.nav-collapse -->
      </div>
      <!--/.container-fluid -->
    </nav>
</body>

</html>