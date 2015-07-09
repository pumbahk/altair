<%inherit file="_base.mako"/>
<div id="table-content">
  <h3>申込詳細</h3>
  <table class="table table-hover">
    <thead>
      <tr>
        <th colspan="4">申込情報</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <th>払込票番号</th>
        <td>${receipt.barcode_no}</td>
        <th>発券ステータス</th>
        <td>
            ${receipt.get_issued_status_in_str}
            % if receipt.canceled_at or receipt.void_at:
                <button type="button" class="btn btn-xs btn-danger">canceled</button>
            % endif
        </td>
      </tr>
      <tr>
        <th>引換票番号</th>
        <td>${receipt.reserve_number}</td>
        <th>入金ステータス</th>
        <td>
            ${receipt.get_payment_status_in_str}
            % if receipt.canceled_at or receipt.void_at:
                <button type="button" class="btn btn-xs btn-danger">canceled</button>
            % endif
        </td>
      </tr>
      <tr>
        <th>管理番号</th>
        <td>${receipt.famiport_order.famiport_order_identifier}</td>
        <th>発券区分</th>
        <td>${receipt.famiport_order.get_type_in_str}</td>
      </tr>
      <tr>
        <th>氏名</th>
        <td>${receipt.famiport_order.customer_name}</td>
        <th>受付日</th>
        <td>${receipt.famiport_order.created_at}</td>
      </tr>
      <tr>
        <th>申込方法</th>
        <td>${receipt.famiport_order.famiport_sales_segment.get_sales_channel_in_str}</td>
        <th>電話番号</th>
        <td>${receipt.famiport_order.customer_phone_number}</td>
      </tr>
    </tbody>

    <thead>
      <tr>
        <th colspan="4">申込内容</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <th>興行コード</th>
        <td colspan="3">${receipt.famiport_order.famiport_sales_segment.famiport_performance.famiport_event.code_1}</td>
      </tr>
      <tr>
        <th>公演名</th>
        <td colspan="3">${receipt.famiport_order.famiport_sales_segment.famiport_performance.name}</td>
      </tr>
      <tr>
        <th>会場</th>
        <td colspan="3">${receipt.famiport_order.famiport_sales_segment.famiport_performance.famiport_event.venue.name}</td>
      </tr>
      <tr>
        <th>公演日時</th>
        <td colspan="3">${receipt.famiport_order.performance_start_at}</td>
      </tr>
      <tr>
        <th>申込サイト</th>
        <td colspan="3">${receipt.famiport_order.famiport_sales_segment.get_sales_channel_in_str}</td>
      </tr>
    </tbody>

    <thead><tr><th colspan="4"></th></tr></thead>
    <tbody>
      <tr>
        <th>料金合計</th>
        <td colspan="3">${receipt.famiport_order.total_amount}</td>
      </tr>
      <tr>
        <th rowspan="3">内訳</th>
        <td colspan="1">チケット代金</td>
        <td colspan="2">${receipt.famiport_order.ticket_payment}</td>
      </tr>
      <tr>
        <td colspan="1">発券手数料</td>
        <td colspan="2">${receipt.famiport_order.ticketing_fee}</td>
      </tr>
      <tr>
        <td colspan="1">システム利用料</td>
        <td colspan="2">${receipt.famiport_order.system_fee}</td>
      </tr>
      <tr>
        <th>レジ支払い金額</th>
        <td colspan="3">${receipt.famiport_order.total_amount}</td>
      </tr>
    </tbody>

    <thead><tr><th colspan="4"></th></tr></thead>
    <tbody>
      <tr>
        <th colspan="1">Famiポート受付日時</th>
        <td colspan="3">${receipt.payment_request_received_at}</td>
      </tr>
      <tr>
        <th>発券日時</th>
        <td>${receipt.famiport_order.issued_at if receipt.famiport_order.issued_at else u'未発券'}</td>
        <th>入金日時</th>
        <td>${receipt.famiport_order.paid_at if receipt.famiport_order.paid_at else u'未入金'}</td>
      </tr>
      % if receipt.famiport_order.type != 2:
      <tr>
        <th>入金店番</th>
        <td>${u"-" if receipt.is_ticketing_receipt else receipt.shop_code}</td>
        <th>入金店舗</th>
        <td>${u"-" if receipt.is_ticketing_receipt else receipt.get_shop_name(request)}</td>
      </tr>
      % endif
      % if receipt.famiport_order.type != 1:
      <tr>
        <th>発券店番</th>
        <td>${u"-" if receipt.is_payment_receipt else receipt.shop_code}</td>
        <th>発券店舗</th>
        <td>${u"-" if receipt.is_payment_receipt else receipt.get_shop_name(request)}</td>
      </tr>
      % endif
      % if receipt.famiport_order.famiport_tickets:
      % for index in range(0,len(receipt.famiport_order.famiport_tickets)):
      <tr>
        <th>バーコード番号${index + 1}</th>
        <td colspan="3">${receipt.famiport_order.famiport_tickets[index].barcode_number}</td>
      </tr>
      % endfor
      % endif
    </tbody>
  </table>
</div>
<div class="buttonBoxBottom pull-right">
  <a href="${request.route_url('rebook_order', action="show", receipt_id=request.matchdict['receipt_id'])}"><button type="button" class="btn btn-info">発券指示</button></a>
</div>
