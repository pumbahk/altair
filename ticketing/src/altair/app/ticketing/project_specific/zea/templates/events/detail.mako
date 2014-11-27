<%inherit file="../base.mako" />
<div class="container">
<table class="table">
  <tbody>
    <tr>
      <th>イベント名</th>
      <td>${_context.event.title}</td>
    </tr>
    <tr>
      <th>申込数</th>
      <td>${_context.orders.count()} (キャンセル: ${_context.canceled_orders.count()} 支払済: ${_context.paid_orders.count()})</td>
    </tr>
  </tbody>
</table>
</div>
<div class="well">
  <a href="${request.path}/download" class="btn btn-primary btn-large">CSVダウンロードする</a>
</div>
<div class="container">
${h.render_bootstrap_pager(paged_orders)}
<table class="table">
  <thead>
    <tr>
      % for column in csvgen.header_row():
      <th>${column}</th>
      % endfor
    </tr>
  </thead>
  <tbody>
    % for order in paged_orders:
    <tr class="${order.status} ${order.payment_status}">
      % for column in csvgen.data_row(order):
      <td>${column}</td>
      % endfor
    </tr>
    % endfor
  </tbody>
</table>
${h.render_bootstrap_pager(paged_orders)}
</div>
