<%inherit file="_base.mako"/>
<div class="jumbotron">
  <form class="form">
    <div class="row">
      <div class="col-md-10">
        <h3 class="form-heading">公演検索</h3>
        <table class="search-table">
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
      <h4>公演検索結果</h4>
    </div>
    <div class="col-md-9 text-center">
      <h4>検索結果件数◯◯件</h4>
    </div>
  </div>
  <table class="table table-hover">
    <thead>
      <tr>
        <th>id</th>
        <th>name</th>
        <th>公演日</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>1</td>
        <td><a href="#">Tokyo公演</a></td>
        <td>2015/6/14</td>
      </tr>
      <tr>
        <td>2</td>
        <td>Osaka公演</td>
        <td>2015/7/14</td>
      </tr>
      <tr>
        <td>3</td>
        <td>Nagoya公演</td>
        <td>2015/8/14</td>
      </tr>
    </tbody>
  </table>
</div>
<div class="buttonBoxBottom pull-right">
  <button type="submit" class="btn btn-info">CSVダウンロード</button>
</div>

<script src="${request.static_url('altair.app.ticketing.famiport.optool:static/js/bootstrap-datepicker.min.js')}"></script>
<script src="${request.static_url('altair.app.ticketing.famiport.optool:static/js/bootstrap-datepicker.ja.min.js')}"></script>
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
