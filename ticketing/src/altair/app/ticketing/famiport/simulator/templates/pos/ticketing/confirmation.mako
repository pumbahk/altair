<%inherit file="/_base.mako" />
<h1>発券確認</h1>
<a href="${request.route_path('pos.ticketing.completion')}">発券する</a>
<div>
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
        <td>${kogyo_name}</td>
      </tr>
      <tr>
        <th>performance_date</th>
        <td>${koen_date}</td>
      </tr>
      <tr>
        <th>barcode_no</th>
        <td>${barcode_no}</td>
      </tr>
      <tr>
        <th>exchange_no</th>
        <td>${exchange_no}</td>
      </tr>
      <tr>
        <th>ticket_count</th>
        <td>${len(tickets)}</td>
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
          <td>${ticket['barcode_no']}</td>
        </tr>
        <tr>
          <th>templateCode</th>
          <td>${ticket['template_code']}</td>
        </tr>
        <tr>
          <th>ticketData</th>
          <td>${ticket['data']}</td>
        </tr>
    % endfor
      </tbody>
    </table>
  % endif
</div>
