<%inherit file="_base.mako"/>

<div class="jumbotron">
  <form class="form" action="${request.route_url('search.receipt')}">
    <div class="row">
      <div class="col-md-10">
        <h3 class="form-heading">申込検索</h3>
        <table class="search-table">
          <tbody>
            <tr>
              <th class="pull-right">${form.barcode_no.label}</th>
              <td>${form.barcode_no(class_='form-control')}</td>
              <th class="pull-right">${form.reserve_number.label}</th>
              <td>${form.reserve_number(class_='form-control')}</td>
            </tr>
            <tr>
              <th class="pull-right">${form.management_number.label}</th>
              <td>${form.management_number(class_='form-control')}</td>
              <th class="pull-right">${form.barcode_number.label}</th>
              <td>${form.barcode_number(class_='form-control')}</td>
            </tr>
            <tr>
              <th class="pull-right">${form.customer_phone_number.label}</th>
              <td>${form.customer_phone_number(class_='form-control')}</td>
              <th class="pull-right">${form.shop_code.label}</th>
              <td>${form.shop_code(class_='form-control')}</td>
            </tr>
            <tr>
              <th class="pull-right">${form.shop_name.label}</th>
              <td>${form.shop_name(class_='form-control')}</td>
              <th class="pull-right"></th>
              <td></td>
            </tr>
            <tr>
                <th class="pull-right">${form.sales_from.label}</th>
                <td colspan="3">
                  <div class="form-inline">
                    <div class="input-group date">
                      ${form.sales_from(class_='form-control')}
                    </div>
                    ~
                    <div class="input-group date">
                      ${form.sales_to(class_='form-control')}
                    </div>
                  </div>
                </td>
             </tr>
          </table>
      </div>
      <div class="col-md-2 buttonBox">
        <button type="reset" class="btn btn-default">Clear<span class="glyphicon glyphicon-erase"></span></button>
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
  % endif
  <a href="#" class="toggle-btn pull-right">残り項目表示</a>
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
        <th>支払期限日時</th>
        <th>発券期限日時</th>
        <th>申込日時</th>
        <th class="first-hidden">電話番号</th>
        <th class="first-hidden">払込票番号</th>
        <th class="first-hidden">引換票番号</th>
        <th class="first-hidden">発券枚数</th>
        <th class="first-hidden">入金日時</th>
        <th class="first-hidden">入金店番</th>
        <th class="first-hidden">入金店名</th>
        <th class="first-hidden">発券日時</th>
        <th class="first-hidden">発券店番</th>
        <th class="first-hidden">発券店名</th>
      </tr>
    </thead>
    % if entries:
    <tbody>
    % for receipt in entries:
      <tr>
        <td><input type="radio" value="${receipt.id}" name="radio_gr"></td>
        <td>${receipt.famiport_order.famiport_sales_segment.name}</td>
        <td>${receipt.famiport_order.get_type_in_str}</td>
        <td>${receipt.get_issued_status_in_str}</td>
        <td>${receipt.get_payment_status_in_str}</td>
        <td>${receipt.famiport_order.famiport_sales_segment.famiport_performance.name}</td>
        <td>${vh.get_date(receipt.famiport_order.famiport_sales_segment.famiport_performance.start_at)}</td>
        <td>${vh.get_time(receipt.famiport_order.famiport_sales_segment.famiport_performance.start_at)}</td>
        <td>${receipt.famiport_order.famiport_order_identifier}</td>
        <td>${receipt.famiport_order.customer_name}</td>
        <td>${receipt.famiport_order.payment_due_at}</td>
        <td>${receipt.famiport_order.ticketing_end_at}</td>
        <td>${receipt.famiport_order.created_at}</td>
        <td class="first-hidden">${receipt.famiport_order.customer_phone_number}</td>
        <td class="first-hidden">${receipt.barcode_no}</td>
        <td class="first-hidden">${receipt.reserve_number}</td>
        <td class="first-hidden">${receipt.famiport_order.ticket_total_count}</td>
        <td class="first-hidden">${receipt.famiport_order.paid_at}</td>
        <td class="first-hidden">${receipt.shop_code}</td>
        <td class="first-hidden">${receipt.get_shop_name(request)}</td>
        <td class="first-hidden">${receipt.famiport_order.issued_at}</td>
        <td class="first-hidden">${receipt.shop_code}</td>
        <td class="first-hidden">${receipt.get_shop_name(request)}</td>
      </tr>
    % endfor
    </tbody>
    % endif
  </table>
</div>
<div class="buttonBoxBottom pull-right">
  <a id="to_rebook" href=""><button type="button" class="btn btn-info">発券指示</button></a>
  <a id="to_detail" href=""><button type="button" class="btn btn-info">申込詳細</button></a>
</div>


<script src="${request.static_url('altair.app.ticketing.famiport.optool:static/js/bootstrap-datepicker.min.js')}"></script>
<script src="${request.static_url('altair.app.ticketing.famiport.optool:static/js/bootstrap-datepicker.ja.min.js')}"></script>
<script type="text/javascript">
    $(document).ready(function(){
      $("*[name=radio_gr]:radio").change(function(){
        var receipt_id = $(this).val();
        $("#to_detail").attr("href", '${request.route_url('receipt.detail', receipt_id='{receipt_id}')}'.replace(encodeURIComponent('{receipt_id}'), receipt_id));
        $("#to_rebook").attr("href", '${request.route_url('rebook_order', action="show", receipt_id='{receipt_id}')}'.replace(encodeURIComponent('{receipt_id}'), receipt_id));
        });
        $('#sales_from').datepicker({
              format: "yyyy-mm-dd",
              language: "ja"
            });
        $('#sales_to').datepicker({
              format: "yyyy-mm-dd",
              language: "ja"
        });
        $('.toggle-btn').on('click', function(e) {
            e.preventDefault();
            console.log('push toggle');
            $('td.first-hidden, th.first-hidden').show();
        });
      });
</script>

