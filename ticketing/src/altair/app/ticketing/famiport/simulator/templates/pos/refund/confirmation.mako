<%inherit file="/_base.mako" />
<h1>払戻確認</h1>
<a href="${request.route_path('pos.refund.completion')}">払い戻す</a>
<table class="table">
  <tbody>
% for i, entry in enumerate(entries):
  % if entry['barCodeNo']:
    <tr>
      <tr>
        <th rowspan="9">#${i + 1}</th>
        <th>barCodeNo</th>
        <td>${entry['barCodeNo']}</td>
      </tr>
      <tr>
        <th>resultCode</th>
        <td>${h.refund_result_code_as_string(entry['resultCode'])}</td>
      </tr>
      % if entry['resultCode'] != u'01':
      <tr>
        <th>mainTitle</th>
        <td>${entry['mainTitle']}</td>
      </tr>
      <tr>
        <th>perfDay</th>
        <td>${entry['perfDay']}</td>
      </tr>
      <tr>
        <th>repayment</th>
        <td>${entry['repayment']}</td>
      </tr>
      <tr>
        <th>refundStart</th>
        <td>${entry['refundStart']}</td>
      </tr>
      <tr>
        <th>refundEnd</th>
        <td>${entry['refundEnd']}</td>
      </tr>
      <tr>
        <th>ticketTyp</th>
        <td>${entry['ticketTyp']}</td>
      </tr>
      <tr>
        <th>charge</th>
        <td>${entry['charge']}</td>
      </tr>
      % endif
  % endif
% endfor
    </tbody>
  </table>
<?div>
