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
    <div class="jumbotron">
      <form class="form re_order_form">
        <div class="row" style="margin-bottom:10px;">
          <h3 class="form-heading">発券方法</h3>
          <div class="form-group">
            <label class="radio-inline">
              <input type="radio" name="optradio"><span class="text-lg">同席番再予約</span>
            </label>
            <label class="radio-inline">
              <input type="radio" name="optradio"><span class="text-lg">再発券</span>
            </label>
          </div>
          <div class="form-group">
            <label for="sel1" class="col-md-2 control-label">理由コード:</label>
            <div class="col-md-10">
              <select class="form-control" id="sel1">
                <option>【910】同席番再予約（店舗都合）</option>
                <option>【911】同席番再予約（お客様都合）</option>
                <option>【912】同席番再予約（強制成立）</option>
                <option>【913】再発券（店舗都合）</option>
                <option>【914】その他</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label for="reason_area" class="col-md-2 control-label">理由備考:</label>
            <div class="col-md-10">
              <textarea class="form-control" rows="3" id="reason_area"></textarea>
            </div>
          </div>
          <div class="form-group">
              <label for="old_num_type" class="col-md-2">旧番号種類:</label>
              <div class="col-md-10">
                <input type="text" class="form-control" id="old_num_type">
              </div>
          </div>
          <div class="form-group">
              <label for="old_num" class="col-md-2">旧番号:</label>
              <div class="col-md-10">
                <input type="text" class="form-control" id="old_num">
              </div>
          </div>
        </div>
        <div class="row pull-right">
          <button type="submit" class="btn btn-default">理由修正</button>
          <button type="button" class="btn btn-default" data-toggle="modal" data-target="#myModal">実行</button>
          <a href="search.html"><button type="button" class="btn btn-default">閉じる</button></a>
        </div>
      </form>
    </div>
    <footer style="text-align:center;">
      <div>&copy; 2012 TicketStar Inc.</div>
      <div>version =</div>
    </footer>
  </div>
  <!-- /container -->

  <!-- Modal -->
  <div class="modal fade" id="myModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
          <h4 class="modal-title" id="myModalLabel">確認</h4>
        </div>
        <div class="modal-body text-center">
          実行してもよろしいですか
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-primary" id="modal_ok">OK</button>
          <button type="button" class="btn btn-default" data-dismiss="modal">キャンセル</button>
        </div>
      </div>
    </div>
  </div>

  <script type="text/javascript">
    $(document).ready(function() {
      $("#modal_ok").on('click', function() {
        $('.modal-title').html('実行結果');
        $('.modal-body').html('正常に終了しました<br><br> 払込票番号が「1」から「2」に変わりました。');
      });
    });
  </script>
</body>

</html>
