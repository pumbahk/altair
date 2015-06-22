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
            <li class="active"><a href="search.html">申込検索</a></li>
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

    <!-- Main component for a primary marketing message or call to action -->
    <div id="table-content">
      <h3>申込詳細</h3>
      <table class="table table-hover">
        <thead>
          <tr>
            <th colspan="4">申込情報</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th>払込票番号</th>
            <td>aaaaaaaaa</td>
            <th>申込ステータス</th>
            <td>bbbbbbbbb</td>
          </tr>
          <tr>
            <th>引換票番号</th>
            <td></td>
            <th>発券区分</th>
            <td></td>
          </tr>
          <tr>
            <th>管理番号</th>
            <td></td>
            <th>受付日</th>
            <td></td>
          </tr>
          <tr>
            <th>氏名</th>
            <td></td>
            <th>氏名カナ</th>
            <td></td>
          </tr>
          <tr>
            <th>申込方法</th>
            <td></td>
            <th>電話番号</th>
            <td></td>
          </tr>
        </tbody>

        <thead>
          <tr>
            <th colspan="4">申込内容</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th>興行コード</th>
            <td colspan="3">aaaaaaaaa</td>
          </tr>
          <tr>
            <th>公演名</th>
            <td colspan="3"></td>
          </tr>
          <tr>
            <th>会場</th>
            <td colspan="3"></td>
          </tr>
          <tr>
            <th>公演日時</th>
            <td colspan="3"></td>
          </tr>
          <tr>
            <th>申込サイト</th>
            <td colspan="3">cccccc</td>
          </tr>
          <tr>
            <th rowspan="2">席種・料金</th>
            <td rowspan="2">aaaa</td>
            <td colspan="2">aaaa</td>
          </tr>
          <tr>
            <td colspan="2">aaaa</td>
          </tr>
        </tbody>

        <thead><tr><th colspan="4"></th></tr></thead>
        <tbody>
          <tr>
            <th>料金合計</th>
            <td colspan="3">aaaaaaaaa</td>
          </tr>
          <tr>
            <th rowspan="3">内訳</th>
            <td colspan="1">チケット代金</td>
            <td colspan="2">333333</td>
          </tr>
          <tr>
            <td colspan="1">発券手数料</td>
            <td colspan="2">111</td>
          </tr>
          <tr>
            <td colspan="1">システム利用料</td>
            <td colspan="2">222</td>
          </tr>
          <tr>
            <th>レジ支払い金額</th>
            <td colspan="3">cccccc</td>
          </tr>
        </tbody>

        <thead><tr><th colspan="4"></th></tr></thead>
        <tbody>
          <tr>
            <th>Famiポート受付日時</th>
            <td>aaaaaaaaa</td>
            <th>発券日時</th>
            <td>aaaaaaaaa</td>
          </tr>
          <tr>
            <th>発券店番</th>
            <td>aaaaaaaaa</td>
            <th>発券店舗</th>
            <td>aaaaaaaaa</td>
          </tr>
          <tr>
            <th>バーコード番号1</th>
            <td colspan="3"></td>
          </tr>
          <tr>
            <th>バーコード番号2</th>
            <td colspan="3"></td>
          </tr>
          <tr>
            <th>バーコード番号3</th>
            <td colspan="3"></td>
          </tr>
          <tr>
            <th>備考</th>
            <td colspan="3"></td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="buttonBoxBottom pull-right">
      <a href="re_order.html"><button type="submit" class="btn btn-info">発券指示</button></a>
      <button type="submit" class="btn btn-info">発券取消</button>
    </div>
    <footer style="text-align:center;">
      <div>&copy; 2012 TicketStar Inc.</div>
      <div>version =</div>
    </footer>
  </div>
  <!-- /container -->
</body>

</html>
