<%inherit file="_base.mako"/>

<div id="table-content">
  <h3>公演詳細</h3>
  <table class="table table-hover">
    <thead>
      <tr>
        <th colspan="2">公演情報</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <th>興行ID</th>
        <td>${performance.famiport_event.id}</td>
      </tr>
      <tr>
        <th>興行コード・サブコード</th>
        <td>${performance.famiport_event.code_1}-${performance.famiport_event.code_2}</td>
      </tr>
      <tr>
        <th>興行名</th>
        <td>${performance.famiport_event.name_1}</td>
      </tr>
      <tr>
        <th>公演名</th>
        <td>${performance.name}</td>
      </tr>
      <tr>
        <th>会場名</th>
        <td>${performance.famiport_event.venue.name}</td>
      </tr>
    </tbody>

    <thead>
      <tr>
        <th colspan="4"></th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <th>開演日</th>
        <td colspan="3">${h.get_date(performance.start_at)}</td>
      </tr>
      <tr>
        <th>開演時刻</th>
        <td colspan="3">${h.get_time(performance.start_at)}</td>
      </tr>
    </tbody>

    <thead><tr><th colspan="4"></th></tr></thead>
    <tbody>
      <tr>
        <th>主催者</th>
        <td colspan="3">${performance.famiport_event.client.name}</td>
      </tr>
    </tbody>
  </table>
</div>
<div class="buttonBoxBottom pull-right">
  <a href=${request.route_url('search.performance')}><button type="submit" class="btn btn-info">戻る</button></a>
</div>
