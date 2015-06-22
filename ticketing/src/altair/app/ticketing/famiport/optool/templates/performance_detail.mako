<!DOCTYPE html>
<html>

<head>
  <title>Famiport</title>
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="viewport" content="width=device-width, maximum-scale=1.0, minimum-scale=1.0" />
  <meta charset="UTF-8" />
  <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css" rel="stylesheet">
  <link href="signin.css" rel="stylesheet">
  <link href="search.css" rel="stylesheet">
  <script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/js/bootstrap.min.js"></script>
  <style media="screen">
    body {
      background-color: #FFF;
    }
    .table tbody th {
      width:25%;
    }
  </style>
</head>

<body>
  <div class="container">
    <!-- Static navbar -->
    <nav class="navbar navbar-default">
      <div class="container-fluid">
        <div class="navbar-header">
          <a class="navbar-brand" href="#"><img src="famiport_logo.jpg" style="width:150px;"/></a>
        </div>
        <div id="navbar" class="navbar-collapse collapse">
          <ul class="nav navbar-nav">
            <li><a href="search.html">申込検索</a></li>
            <li><a href="search_per_store.html">店舗別申込検索</a></li>
            <li class="active"><a href="#">公演検索</a></li>
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

    <!-- Main component for a primary marketing message or call to action -->
    <div id="table-content">
      <h3>公演詳細</h3>
      <table class="table table-hover">
        <thead>
          <tr>
            <th>公演情報</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th>興行ID</th>
            <td>aaaaaaaaa</td>
          </tr>
          <tr>
            <th>興行コード・サブコード</th>
            <td ></td>
          </tr>
          <tr>
            <th>興行名</th>
            <td ></td>
          </tr>
          <tr>
            <th>公演名</th>
            <td ></td>
          </tr>
          <tr>
            <th>会場名</th>
            <td></td>
          </tr>
        </tbody>

        <thead>
          <tr>
            <th colspan="4"></th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th>開演日</th>
            <td colspan="3">aaaaaaaaa</td>
          </tr>
          <tr>
            <th>開場時刻</th>
            <td colspan="3"></td>
          </tr>
          <tr>
            <th>開演時刻</th>
            <td colspan="3"></td>
          </tr>
          <tr>
            <th>終演時刻</th>
            <td colspan="3"></td>
          </tr>
          <tr>
            <th>申込サイト</th>
            <td colspan="3">cccccc</td>
          </tr>
        </tbody>

        <thead><tr><th colspan="4"></th></tr></thead>
        <tbody>
          <tr>
            <th>主催者</th>
            <td colspan="3">aaaaaaaaa</td>
          </tr>
          <tr>
            <th>注意事項</th>
            <td colspan="3">aaaaaaaaa</td>
          </tr>
          <tr>
            <th>Famiポート注意事項</th>
            <td colspan="3">aaaaaaaaa</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="buttonBoxBottom pull-right">
      <a href="search_performance.html"><button type="submit" class="btn btn-info">戻る</button></a>
    </div>
    <footer style="text-align:center;">
      <div>&copy; 2012 TicketStar Inc.</div>
      <div>version =</div>
    </footer>
  </div>
  <!-- /container -->
</body>

</html>
