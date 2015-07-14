<%inherit file="_base.mako"/>
<div id="table-content">
  <h3>払戻公演詳細</h3>
  <table class="table table-hover">
    <thead>
      <tr>
        <th colspan="4">払戻公演詳細情報</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <th colspan="1">興行コード・サブコード</th>
        <td colspan="3">${performance.famiport_event.code_1}-${performance.famiport_event.code_2}</td>
      </tr>
      <tr>
        <th colspan="1">興行名</th>
        <td colspan="3">${performance.famiport_event.name_1}</td>
      </tr>
      <tr>
        <th colspan="1">公演日時</th>
        <td colspan="3">${vh.format_datetime(performance.start_at)}</td>
      </tr>
      <tr>
        <th colspan="1">会場名</th>
        <td colspan="3">${performance.famiport_event.venue.name}</td>
      </tr>
      <tr>
        <th colspan="1">払戻開始日〜払戻終了日</th>
        <td colspan="3">${vh.format_date(refund_entry.famiport_refund.start_at)}〜${vh.format_date(refund_entry.famiport_refund.end_at)}</td>
      </tr>
      <tr>
        <th colspan="1">プレイガイド必着日</th>
        <td colspan="3">${vh.format_date(refund_entry.famiport_refund.send_back_due_at)}</td>
      </tr>
    </tbody>
  </table>
</div>
