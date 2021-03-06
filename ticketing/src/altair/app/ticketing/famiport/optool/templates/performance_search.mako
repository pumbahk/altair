<%inherit file="_base.mako"/>
<div class="jumbotron">
  <form class="form" action="${request.route_path('search.performance')}">
    <div class="row">
      <div class="col-md-10">
        <h3 class="form-heading">公演検索</h3>
        <table class="search-table">
          <tr>
            <th class="pull-right">${form.event_id.label}</th>
            <td>${form.event_id(class_='form-control')}</td>
            <th class="pull-right">${form.event_code_1.label}</th>
            <td>${form.event_code_1(class_='form-control',placeholder='main-code')}</td>
            <td>${form.event_code_2(class_='form-control',placeholder='sub-code')}</td>
          </tr>
          <tr>
            <th class="pull-right">${form.event_name_1.label}</th>
            <td>${form.event_name_1(class_='form-control')}</td>
            <th class="pull-right">${form.performance_name.label}</th>
            <td>${form.performance_name(class_='form-control')}</td>
          </tr>
          <tr>
            <th class="pull-right">${form.venue_name.label}</th>
            <td colspan="1">${form.venue_name(class_='form-control')}</td>
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
        <button type="reset" class="btn btn-default reset-btn">クリア<span class="glyphicon glyphicon-erase"></span></button>
        <button type="submit" class="btn btn-lg btn-default">検索
          <span class="glyphicon glyphicon-search"></span>
        </button>
      </div>
    </div>
  </form>
</div>
<div id="table-content">
  % if performances:
  <div class="row">
    <div class="col-md-3 text-center">
      <h4>公演検索結果</h4>
    </div>
    <div class="col-md-9 text-left">
      <h4>検索結果件数${performances.item_count}件</h4>
    </div>
  </div>
  ${performances.pager(link_attr={"class": "btn small"}, curpage_attr={"class": "btn primary small disabled"})}
  <table class="table table-hover">
    <thead>
      <tr>
        <th>興行ID</th>
        <th>興行コード・サブコード</th>
        <th>興行名</th>
        <th>公演名</th>
        <th>公演日</th>
        <th>会場名</th>
      </tr>
    </thead>
    <tbody>
      % for performance in performances:
      <tr>
        <td>${performance.famiport_event_id}</td>
        <td>${performance.famiport_event.code_1}-${performance.famiport_event.code_2}</td>
        <td>${performance.famiport_event.name_1}</td>
        <td><a href="${request.route_url('performance.detail', performance_id=performance.id)}">${performance.name}</a></td>
        <td>${vh.format_date(performance.start_at)}</td>
        <td>${performance.famiport_event.venue.name}</td>
      </tr>
      % endfor
    </tbody>
  </table>
  % else:
    <p>検索条件にマッチする公演はありません</p>
  % endif
</div>

<script src="${request.static_url('altair.app.ticketing.famiport.optool:static/js/bootstrap-datepicker.min.js')}"></script>
<script src="${request.static_url('altair.app.ticketing.famiport.optool:static/js/bootstrap-datepicker.ja.min.js')}"></script>
<script type="text/javascript">
      $(document).ready(function () {
            $('#performance_from').datepicker({
              format: "yyyy-mm-dd",
              language: "ja",
              autoclose: true
            });
            $('#performance_to').datepicker({
              format: "yyyy-mm-dd",
              language: "ja",
              autoclose: true
            });
            $('.reset-btn').click(function() {
                $('.search-table input').attr('value', '');
            });
      });
</script>
