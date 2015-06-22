<!DOCTYPE html>
<html>

<%include file="header.mako"/>

<body>
  <div class="container">
    <!-- Static navbar -->
    <nav class="navbar navbar-default">
      <div class="container-fluid">
        <div class="navbar-header">
          <a class="navbar-brand" href="#"><img src="${request.static_url('altair.app.ticketing.famiport.optool:static/images/famiport_logo.jpg')}" style="width:150px;"/></a>
        </div>
        <div id="navbar" class="navbar-collapse collapse">
          <ul class="nav navbar-nav">
            <li><a href="search.html">申込検索</a></li>
            <li><a href="search_per_store.html">店舗別申込検索</a></li>
            <li><a href="search_performance.html">公演検索</a></li>
            <li class="active"><a href="#">払戻公演データ検索</a></li>
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
            <h3 class="form-heading">払戻公演検索</h3>
            <table class="search-table">
              <tr>
                <td colspan="4">
                  <div class="form-group">
                    <label class="radio-inline">
                      <input type="checkbox" name="chkbox"><span class="text-lg">払戻期間前</span>
                    </label>
                    <label class="radio-inline">
                      <input type="checkbox" name="chkbox"><span class="text-lg">払戻期間中</span>
                    </label>
                    <label class="radio-inline">
                      <input type="checkbox" name="chkbox"><span class="text-lg">払戻期間中</span>
                    </label>
                  </div>
                </td>
              </tr>
              <tr>
                <th class="pull-right"><label class="control-label">公開日：</label></th>
                <td colspan="3">
                  <div class="form-inline">
                    <div class="input-group date">
                      <input type="text" size="20" class="form-control" id="datepicker1" data-provide="datapiker">
                    </div>
                    ~
                    <div class="input-group date">
                      <input type="text" size="20" class="form-control" id="datepicker2" data-provide="datapiker">
                    </div>
                  </div>
                </td>
              </tr>
            </table>
          </div>
          <div class="buttonBox col-md-2">
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
          <h4>払戻公演検索結果一覧</h4>
        </div>
        <div class="col-md-9 text-center">
          <h4>検索結果件数◯◯件</h4>
        </div>
      </div>
      <table class="table table-hover">
        <thead>
          <tr>
            <th>興行コード・サブコード</th>
            <th>興行名</th>
            <th>公演日</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><a href="search_payback_ticket.html">1111-1111</a></td>
            <td><a href="payback_per_detail.html">Tokyo公演</a></td>
            <td>2015/6/14</td>
          </tr>
          <tr>
            <td>2222-2222</td>
            <td>Osaka公演</td>
            <td>2015/7/14</td>
          </tr>
          <tr>
            <td>3333-3333</td>
            <td>Nagoya公演</td>
            <td>2015/8/14</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="buttonBoxBottom pull-right">
      <button type="submit" class="btn btn-info">CSVダウンロード</button>
    </div>
    <footer style="text-align:center;">
      <div>&copy; 2012 TicketStar Inc.</div>
      <div>version =</div>
    </footer>
  </div>
  <!-- /container -->
</div>
<script src="bootstrap-datepicker.min.js"></script>
<script src="bootstrap-datepicker.ja.min.js"></script>
<script type="text/javascript">
      $(document).ready(function () {
            $('#datepicker1').datepicker({
              format: "yyyy-mm-dd",
              language: "ja"
            });
            $('#datepicker2').datepicker({
              format: "yyyy-mm-dd",
              language: "ja"
            });
      });
</script>
</body>

</html>
