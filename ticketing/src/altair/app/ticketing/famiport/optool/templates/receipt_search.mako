<%inherit file="_base.mako"/>

<div class="jumbotron">
  <form class="form" action="${request.route_path('search.receipt')}" method='POST'>
    <div class="row">
      <div class="col-md-10">
        <h3 class="form-heading">申込検索</h3>
        <table class="search-table">
          <tbody>
            <tr>
              <th class="pull-right">${form.barcode_no.label}</th>
              <td>${form.barcode_no(class_='form-control')}</td>
              <th class="pull-right">${form.exchange_number.label}</th>
              <td>${form.exchange_number(class_='form-control')}</td>
            </tr>
            <tr>
              <th class="pull-right">${form.famiport_order_identifier.label}</th>
              <td>${form.famiport_order_identifier(class_='form-control')}</td>
              <th class="pull-right">${form.barcode_number.label}</th>
              <td>${form.barcode_number(class_='form-control')}</td>
            </tr>
            <tr>
              <th class="pull-right">${form.customer_phone_number.label}</th>
              <td>${form.customer_phone_number(class_='form-control')}</td>
              <th class="pull-right">${form.shop_code.label}</th>
              <td>${form.shop_code(class_='form-control')}</td>
            </tr>
          </table>
      </div>
      <div class="col-md-2 buttonBox">
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
      <h4>申込検索結果一覧</h4>
    </div>
    <div class="col-md-9 text-left">
      % if count:
      <h4>検索結果件数${count}件</h4>
      % endif
    </div>
  </div>
  % if entries:
  ${entries.pager()}
  <table class="table table-hover">
    <thead>
      <tr>
        <th>選択</th>
        <th>申込区分</th>
        <th>発券区分</th>
        <th>申込ステータス</th>
        <th>入金ステータス</th>
        <th>興行名</th>
        <th>公演日</th>
        <th>開演時間</th>
        <th>管理番号</th>
        <th>氏名</th>
        <th>電話番号</th>
        <th>払込票番号</th>
        <th>引換票番号</th>
        <th>発券枚数</th>
        <th>入金日時</th>
        <th>入金店番</th>
        <th>入金店名</th>
        <th>発券日時</th>
        <th>発券店番</th>
        <th>発券店名</th>
        <th>支払期限日時</th>
        <th>発券期限日時</th>
        <th>申込日時</th>
      </tr>
    </thead>
    <tbody>
    % for receipt in entries:
      <tr>
        <td><input type="radio" value="${receipt.id}" name="radio_gr" form="order"></td>
        <td>${receipt.famiport_order.famiport_sales_segment.name}</td>
        <td>${receipt.famiport_order.get_type_in_str}</td>
        <td>${receipt.famiport_order.get_issued_status_in_str}</td>
        <td>${u'入金済み' if receipt.famiport_order.paid_at else u'入金待ち'}</td>
        <td>${receipt.famiport_order.famiport_sales_segment.famiport_performance.name}</td>
        <td>${vh.get_date(receipt.famiport_order.famiport_sales_segment.famiport_performance.start_at)}</td>
        <td>${vh.get_time(receipt.famiport_order.famiport_sales_segment.famiport_performance.start_at)}</td>
        <td>${receipt.famiport_order.famiport_order_identifier}</td>
        <td>${receipt.famiport_order.customer_name}</td>
        <td>${receipt.famiport_order.customer_phone_number}</td>
        <td>${receipt.barcode_no}</td>
        <td><span style="color:red;">exchange_number?</span></td>
        <td>${receipt.famiport_order.ticket_total_count}</td>
        <td>${receipt.famiport_order.paid_at}</td>
        <td>${receipt.shop_code}</td>
        <td>${receipt.get_shop_name(request)}</td>
        <td>${receipt.famiport_order.issued_at}</td>
        <td>${receipt.shop_code}</td>
        <td>${receipt.get_shop_name(request)}</td>
        <td>${receipt.famiport_order.payment_due_at}</td>
        <td>${receipt.famiport_order.ticketing_end_at}</td>
        <td>${receipt.famiport_order.created_at}</td>
      </tr>
    % endfor
    </tbody>
  </table>
  % endif
</div>
<div class="buttonBoxBottom pull-right">
  <a id="to_rebook" href=""><button type="button" class="btn btn-info">発券指示</button></a>
  <button type="button" class="btn btn-info">CSVダウンロード</button>
  <a id="to_detail" href=""><button type="button" class="btn btn-info">申込詳細</button></a>
</div>

  <script type="text/javascript">
    $(document).ready(function(){
      $("*[name=radio_gr]:radio").change(function(){
        var receipt_id = $(this).val();
        $("#to_detail").attr("href", '${request.route_url('receipt.detail', receipt_id='{receipt_id}')}'.replace(encodeURIComponent('{receipt_id}'), receipt_id));
        $("#to_rebook").attr("href", '${request.route_url('rebook_order', action="show", order_id='{receipt_id}')}'.replace(encodeURIComponent('{receipt_id}'), receipt_id));
        });
      });
  </script>

