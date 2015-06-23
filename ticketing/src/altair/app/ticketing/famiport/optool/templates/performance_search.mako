<%inherit file="_base.mako"/>
<div class="jumbotron">
  <form class="form" action="${request.route_path('search.performance')}" method='POST'>
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
            <th class="pull-right">${form.event_name.label}</th>
            <td>${form.event_name(class_='form-control')}</td>
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
        <button type="button" class="btn btn-default">Clear<span class="glyphicon glyphicon-erase"></span></button>
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
    % if count:
    <div class="col-md-9 text-center">
      <h4>検索結果件数${count}件</h4>
    </div>
    % endif
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
