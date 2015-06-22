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
  <script src="jquery-1.11.3.min.js"></script>
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

    <!-- Main component for a primary marketing message or call to action -->
    <div class="jumbotron">
      <form class="form">
        <div class="row">
          <div class="col-md-10">
            <h3 class="form-heading">申込検索</h3>
            <table class="search-table">
              <tbody>
                <tr>
                  <th>
                    <label class="pull-right">払込票番号：</label>
                  </th>
                  <td>
                    <input type="text" name="payment_num" class="form-control" autofocus>
                  </td>
                  <th>
                    <label class="pull-right">引換票番号：</label>
                  </th>
                  <td>
                    <input type="text" name="hikikae_num" class="form-control">
                  </td>
                </tr>
                <tr>
                  <th>
                    <label class="pull-right">管理番号：</label>
                  </th>
                  <td>
                    <input type="text" name="control_num" class="form-control">
                  </td>
                  <th>
                    <label class="pull-right">バーコード番号：</label>
                  </th>
                  <td>
                    <input type="text" name="barcode" class="form-control">
                  </td>
                </tr>
                <tr>
                  <th>
                    <label class="pull-right">電話番号：</label>
                  </th>
                  <td>
                    <input type="text" name="tel" class="form-control">
                  </td>
                  <th>
                    <label class="pull-right">店番：</label>
                  </th>
                  <td>
                    <input type="text" name="store_num" class="form-control">
                  </td>
                </tr>
              </table>
          </div>
          <div class="col-md-2 buttonBox">
            <button type="submit" class="btn btn-default">Clear<span class="glyphicon glyphicon-erase"></span></button>
            <button type="submit" class="btn btn-lg btn-default">Search
              <span class="glyphicon glyphicon-search"></span>
            </button>
          </div>
        </div>
      </form>
    </div>
    <div id="table-content">
      <div class="row">
        <div class="col-md-3 text-center">
          <h4>申込検索結果一覧</h4>
        </div>
        <div class="col-md-9 text-center">
          <h4>検索結果件数◯◯件</h4>
        </div>
      </div>
      <table class="table table-hover">
        <thead>
          <tr>
            <th>選択</th>
            <th>申込区分</th>
            <th>興行名</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><input type="radio" value="1" name="radio_gr" form="order"></td>
            <td>一般販売</td>
            <td>鹿島vs横浜（一般販売）</td>
          </tr>
          <tr>
            <td><input type="radio" value="2" name="radio_gr" form="order"></td>
            <td>先行抽選</td>
            <td>鹿島vs横浜（先行抽選）</td>
          </tr>
          <tr>
            <td><input type="radio" value="3" name="radio_gr" form="order"></td>
            <td>あああ</td>
            <td>いいい</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="buttonBoxBottom pull-right">
      <form id="order">
      <a href="re_order.html"><button type="button" class="btn btn-info">発券指示</button></a>
      <button type="submit" class="btn btn-info">発券取消</button>
      <button type="submit" class="btn btn-info">CSVダウンロード</button>
      <a id="to_detail" href=""><button type="button" class="btn btn-info">申込詳細</button></a>
      </form>
    </div>
    <footer style="text-align:center;">
      <div>&copy; 2012 TicketStar Inc.</div>
      <div>version =</div>
    </footer>
  </div>
  <script type="text/javascript">
    $(document).ready(function(){
      $("*[name=radio_gr]:radio").change(function(){
        switch ($(this).val()){
          case "1":
            $("#to_detail").attr("href","order_detail.html");
            break;
          case "2":
            $("#to_detail").attr("href","lots_detail.html");
            break;
          case "3":
            console.log("3");
            break;
        }
      });
    });
  </script>
  <!-- /container -->
</body>

</html>
