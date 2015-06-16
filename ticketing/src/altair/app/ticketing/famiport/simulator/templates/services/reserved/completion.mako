<%inherit file="/_base.mako" />
<h1>完了画面</h1>
<div>
  <p>レシートをレジにお持ちください。</p>
  <table class="table">
    <tbody>
      <tr>
        <th>total_amount</th>
        <td>${total_amount}</td>
      </tr>
      <tr>
        <th>system_fee</th>
        <td>${system_fee}</td>
      </tr>
      <tr>
        <th>ticket_payment</th>
        <td>${ticket_payment}</td>
      </tr>
      <tr>
        <th>ticketing_fee</th>
        <td>${ticketing_fee}</td>
      </tr>
      <tr>
        <th>performance_name</th>
        <td>${performance_name}</td>
      </tr>
      <tr>
        <th>performance_date</th>
        <td>${performance_date}</td>
      </tr>
      <tr>
        <th>barcode_no</th>
        <td>${barcode_no}</td>
      </tr>
      <tr>
        <th>ticket_count</th>
        <td>${ticket_count}</td>
      </tr>
      <tr>
        <th>ticket_count_total</th>
        <td>${ticket_count_total}</td>
      </tr>
    </tbody>
  </table>
</div>
<div>
  <h2>チケット</h2>
  % if not tickets:
  <div class="alert alert-danger">
    チケットが1枚もない予約です！！
  </div>
  % else:
    <table class="table">
      <tbody>
    % for i, ticket in enumerate(tickets):
        <tr>
          <th rowspan="3">${i}</th>
          <th>barCodeNo</th>
          <td>${ticket['barCodeNo']}</td>
        </tr>
        <tr>
          <th>templateCode</th>
          <td>${ticket['templateCode']}</td>
        </tr>
        <tr>
          <th>ticketData</th>
          <td>${ticket['ticketData']}</td>
        </tr>
    % endfor
      </tbody>
    </table>
  % endif

