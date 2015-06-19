<%inherit file="/_base.mako" />
<style type="text/css">
.void { text-decoration: line-through; color: #ccc; }
</style>
<h1>FDCセンター取引操作</h1>
<form action="${request.route_path('fdccenter.service.transaction.cancel')}" method="POST">
<div class="nav-bar">
  <select name="cancel_code">
    % for value, display_name in cancel_code_list:
    <option value="${value}">${display_name}</option>
    % endfor
  </select>
  <button type="submit" class="btn" name="do_cancel">取消する</button>
</div>
<table class="table">
  <thead>
    <tr>
      <th>✔️</th>
      <th>ID</th>
      <th>予約ID</th>
      <th>店舗コード</th>
      <th>クライアントコード</th>
      <th>払込票番号</th>
      <th>引換票番号</th>
      <th>金額</th>
      <th>興行名</th>
      <th>公演日</th>
      <th>発券期間</th>
      <th>支払日時</th>
      <th>発券日時</th>
    </tr>
  </thead>
  <tbody>
% for order in orders:
    <tr${u' class="void"' if order.voided_at else u''|n}>
      <td><input type="checkbox" name="order_id" value="${order.id}" /></td>
      <td>${order.id}</td>
      <td>${order.order_id}</td>
      <td>${order.store_code} (${order.mmk_no})</td>
      <td>${order.client_code}</td>
      <td>${order.barcode_no}</td>
      <td>${order.exchange_no}</td>
      <td>${order.total_amount}</td>
      <td>${order.kogyo_name}</td>
      <td>${order.koen_date}</td>
      <td>${order.ticketing_start_at}〜${order.ticketing_end_at}</td>
      <td>${order.paid_at}</td>
      <td>${order.issued_at}</td>
    </tr>
% endfor
  </tbody>
</table>
</form>
