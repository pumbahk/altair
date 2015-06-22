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
            <li class="active"><a href="search_payback.html">払戻公演データ検索</a></li>
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
      <h3>払戻公演詳細</h3>
      <table class="table table-hover">
        <thead>
          <tr>
            <th colspan="2">払戻公演詳細情報</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th>公演ステータス</th>
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
            <th>公演日時</th>
            <td ></td>
          </tr>
          <tr>
            <th>会場名</th>
            <td></td>
          </tr>
          <tr>
            <th>払戻理由</th>
            <td></td>
          </tr>
          <tr>
            <th>払戻開始日〜払戻終了日</th>
            <td></td>
          </tr>
          <tr>
            <th>プライガイド必着日</th>
            <td></td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="buttonBoxBottom pull-right">
      <a href="search_payback.html"><button type="submit" class="btn btn-info">閉じる</button></a>
    </div>
    <footer style="text-align:center;">
      <div>&copy; 2012 TicketStar Inc.</div>
      <div>version =</div>
    </footer>
  </div>
  <!-- /container -->
</body>

</html>
