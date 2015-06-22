<!DOCTYPE html>
<html>

<%include file="header.mako"/>

<body>
  <div class="container">
    <%include file="menu.mako"/>
    <!-- Main component for a primary marketing message or call to action -->
      <div class="jumbotron">
        <form class="form">
          <div class="row">
            <div class="col-md-10">
              <h3 class="form-heading">払戻チケットデータ検索</h3>
              <table class="search-table">
                <thead><tr><th colspan="4">払戻対象公演</th></tr></thead>
                <tbody>
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
                </tbody>
                <thead><tr><th colspan="4">データ種別</th></tr></thead>
                <tbody>
                <tr>
                  <td colspan="4">
                    <div class="form-group">
                      <label class="radio-inline">
                        <input type="checkbox" name="chkbox"><span class="text-lg">払戻予定</span>
                      </label>
                      <label class="radio-inline">
                        <input type="checkbox" name="chkbox"><span class="text-lg">受付済</span>
                      </label>
                      <label class="radio-inline">
                        <input type="checkbox" name="chkbox"><span class="text-lg">回収済</span>
                      </label>
                      <label class="radio-inline">
                        <input type="checkbox" name="chkbox"><span class="text-lg">未回収</span>
                      </label>
                      <label class="radio-inline">
                        <input type="checkbox" name="chkbox"><span class="text-lg">条件無</span>
                      </label>
                    </div>
                  </td>
                </tr>
                </tbody>
                <tr>
                  <th class="pull-right"><label>興行ID：</label></th>
                  <td><input type="text" name="event_id" class="form-control" autofocus></td>
                  <th class="pull-right"><label>興行コード・サブコード：</label></th>
                  <td><input type="text" name="event_code" class="form-control"></td>
                </tr>
                <tr>
                  <th class="pull-right"><label>興行名：</label></th>
                  <td><input type="text" name="event_name" class="form-control"></td>
                  <th class="pull-right"><label>公演名：</label></th>
                  <td><input type="text" name="performance_name" class="form-control"></td>
                </tr>
                <tr>
                  <th class="pull-right"><label>会場名：</label></th>
                  <td colspan="1"><input type="text" name="venue_name" class="form-control"></td>
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
          <h4>払戻チケット一覧</h4>
        </div>
        <div class="col-md-9 text-center">
          <h4>検索結果件数◯◯件</h4>
        </div>
      </div>
      <table class="table table-hover">
        <thead>
          <tr>
            <th>選択</th>
            <th>払戻状況</th>
            <th>地区</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><input type="radio" value="1" name="radio_gr" form="order"></td>
            <td>済</td>
            <td>01</td>
          </tr>
          <tr>
            <td><input type="radio" value="2" name="radio_gr" form="order"></td>
            <td></td>
            <td>02</td>
          </tr>
          <tr>
            <td><input type="radio" value="3" name="radio_gr" form="order"></td>
            <td>済</td>
            <td>03</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="buttonBoxBottom pull-right">
      <button type="button" class="btn btn-info" data-toggle="modal" data-target="#myModal">払戻取消</button>
      <button type="submit" class="btn btn-info">CSVダウンロード</button>
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
          払戻取消を実行してもよろしいですか
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-primary" id="modal_ok">OK</button>
          <button type="button" class="btn btn-default" data-dismiss="modal">キャンセル</button>
        </div>
      </div>
    </div>
  </div>
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
            $("#modal_ok").on('click', function() {
              $('.modal-title').html('実行結果');
              $('.modal-body').html('払戻取消は正常に行われました');
              $('.modal-footer').html('<button type="button" class="btn btn-default" data-dismiss="modal">閉じる</button>');
            });
      });
</script>
</body>

</html>
