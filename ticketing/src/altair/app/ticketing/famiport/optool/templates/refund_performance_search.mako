<%inherit file="_base.mako"/>
<div class="jumbotron">
  <form class="form" action="${request.route_url('search.refund_performance')}" method='POST'>
    <div class="row">
      <div class="col-md-10">
        <h3 class="form-heading">払戻公演検索</h3>
        <table class="search-table">
          <tr>
            <th class="pull-right">払戻期間：</th>
            <td colspan="3">
              <div class="form-group">
                ${form.before_refund()}
                <span class="text-lg">${form.before_refund.label}</span>
                ${form.during_refund()}
                <span class="text-lg">${form.during_refund.label}</span>
                ${form.after_refund()}
                <span class="text-lg">${form.after_refund.label}</span>
              </div>
            </td>
          </tr>
          <tr>
            <th class="pull-right">${form.performance_from.label}</th>
            <td colspan="3">
              <div class="form-inline">
                <div class="input-group date">
                  ${form.performance_from(class_='form-control')}
                </div>
                ~
                <div class="input-group date">
                  ${form.performance_to(class_='form-control')}
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
    % if count:
    <div class="col-md-9 text-center">
      <h4>検索結果件数${count}件</h4>
    </div>
    % endif
  </div>
  <table class="table table-hover">
    <thead>
      <tr>
        <th>興行コード・サブコード</th>
        <th>興行名</th>
        <th>受付コード</th>
        <th>公演日</th>
        <th>開演時間</th>
        <th>払戻開始日</th>
        <th>払戻終了日</th>
        <th>プレイガイド必着日</th>
      </tr>
    </thead>
    % if entries:
    <tbody>
    % for performance in entries:
      <tr>
        <td><a href="">${performance.famiport_event.code_1}-${performance.famiport_event.code_2}</a></td>
        <td><a href="${request.route_url('refund_performance.detail', performance_id=performance.id)}">${performance.name}</a></td>
        <td></td>
        <td>${vh.get_date(performance.start_at)}</td>
        <td>${vh.get_time(performance.start_at)}</td>
        <td><span style="color:red;">要確認</span></td>
        <td><span style="color:red;">要確認</span></td>
        <td><span style="color:red;">要確認</span></td>
      </tr>
    % endfor
    </tbody>
    % endif
  </table>
</div>

<script src="${request.static_url('altair.app.ticketing.famiport.optool:static/js/bootstrap-datepicker.min.js')}"></script>
<script src="${request.static_url('altair.app.ticketing.famiport.optool:static/js/bootstrap-datepicker.ja.min.js')}"></script>
<script type="text/javascript">
      $(document).ready(function () {
            $('#performance_from').datepicker({
              format: "yyyy-mm-dd",
              language: "ja"
            });
            $('#performance_to').datepicker({
              format: "yyyy-mm-dd",
              language: "ja"
            });
      });
</script>
