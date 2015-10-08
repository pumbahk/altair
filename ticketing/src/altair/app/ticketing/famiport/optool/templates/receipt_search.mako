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
                <th class="pull-right">${form.completed_from.label}</th>
                <td colspan="3">
                  <div class="form-inline">
                    <div class="input-group date">
                      ${form.completed_from(class_='form-control')}
                    </div>
                    ~
                    <div class="input-group date">
                      ${form.completed_to(class_='form-control')}
                    </div>
                  </div>
                </td>
             </tr>
          </table>
      </div>
      <div class="col-md-2 buttonBox">
        <button type="reset" class="btn btn-default reset-btn">クリア<span class="glyphicon glyphicon-erase"></span></button>
        <button type="submit" class="btn btn-lg btn-default">検索
          <span class="glyphicon glyphicon-search"></span>
        </button>
      </div>
    </div>
  </form>
</div>
<div id="table-content">
  % if paginator:
  <div class="row">
    <div class="col-md-3 text-center">
      <h4>申込検索結果一覧</h4>
    </div>
    <div class="col-md-9 text-left">
      <h4>検索結果件数${paginator.item_count}件</h4>
    </div>
  </div>
  ${paginator.pager(link_attr={"class": "btn small"}, curpage_attr={"class": "btn primary small disabled"})}
  <% personal_info = request.context.user.has_perm_for_personal_info %>
  <a href="#" class="toggle-btn pull-right">残り項目表示</a>
  <table class="table table-hover">
    <thead>
      <tr>
        <th nowrap="nowrap">選択</th>
        <th nowrap="nowrap">申込区分</th>
        <th nowrap="nowrap">発券区分</th>
        <th nowrap="nowrap">申込ステータス</th>
        <th nowrap="nowrap">入金ステータス</th>
        <th nowrap="nowrap">興行名</th>
        <th nowrap="nowrap">公演日</th>
        <th nowrap="nowrap">開演時間</th>
        <th nowrap="nowrap">管理番号</th>
        <th nowrap="nowrap">払込票番号</th>
        <th nowrap="nowrap">引換票番号</th>
        % if personal_info:
        <th nowrap="nowrap">氏名</th>
        % endif
        <th nowrap="nowrap">支払期限日時</th>
        <th nowrap="nowrap">発券期限日時</th>
        <th nowrap="nowrap">申込日時</th>
        <th nowrap="nowrap">Altair受付番号</th>
        % if personal_info:
        <th nowrap="nowrap" class="first-hidden">電話番号</th>
        % endif
        <th nowrap="nowrap" class="first-hidden">発券枚数</th>
        <th nowrap="nowrap" class="first-hidden">入金日時</th>
        <th nowrap="nowrap" class="first-hidden">入金店番</th>
        <th nowrap="nowrap" class="first-hidden">入金店名</th>
        <th nowrap="nowrap" class="first-hidden">発券日時</th>
        <th nowrap="nowrap" class="first-hidden">発券店番</th>
        <th nowrap="nowrap" class="first-hidden">発券店名</th>
      </tr>
    </thead>
    <tbody>
    % for receipt in paginator.items:
      <tr>
        <td><input type="radio" value="${receipt.id}" name="radio_gr"></td>
        <td nowrap="nowrap">
            ${receipt.famiport_order.famiport_sales_segment.name if receipt.famiport_order.famiport_sales_segment else u'-'}
            % if receipt.canceled_at:
                <br><button type="button" class="btn btn-danger btn-xs">canceled</button>
            % elif receipt.void_at and receipt.void_reason == 99:
                <br><button type="button" class="btn btn-warning btn-xs">再発券</button>
            % endif
        </td>
        <td nowrap="nowrap">${receipt.famiport_order.get_type_in_str}</td>
        <td nowrap="nowrap">${receipt.get_issued_status_in_str}</td>
        <td nowrap="nowrap">${receipt.get_payment_status_in_str}</td>
        <td nowrap="nowrap">${receipt.famiport_order.famiport_performance.name}</td>
        <td nowrap="nowrap">${vh.format_date(receipt.famiport_order.famiport_performance.start_at)}</td>
        <td nowrap="nowrap">${vh.format_time(receipt.famiport_order.famiport_performance.start_at)}</td>
        <td nowrap="nowrap">${vh.format_famiport_order_identifier(receipt.famiport_order_identifier)}</td>
        <td nowrap="nowrap">${vh.get_barcode_no_text(receipt.barcode_no)}</td>
        <td nowrap="nowrap">${receipt.reserve_number}</td>
        % if personal_info:
        <td nowrap="nowrap">${receipt.famiport_order.customer_name}</td>
        % endif
        <td nowrap="nowrap">${vh.format_date(receipt.famiport_order.payment_due_at)}</td>
        <td nowrap="nowrap">${vh.format_date(receipt.famiport_order.ticketing_end_at)}</td>
        <td nowrap="nowrap">${vh.format_date(receipt.famiport_order.created_at)}</td>
        <td nowrap="nowrap">${receipt.famiport_order.order_no}</td>
        % if personal_info:
        <td class="first-hidden">${receipt.famiport_order.customer_phone_number}</td>
        % endif
        <% payment_shop_code = vh.display_payment_shop_code(receipt) %>
        <% delivery_shop_code = vh.display_delivery_shop_code(receipt) %>
        <% disp_payment_date = vh.display_payment_date(receipt) %>
        <% disp_delivery_date = vh.display_delivery_date(receipt) %>
        <td nowrap="nowrap" class="first-hidden">${receipt.famiport_order.ticket_total_count}</td>
        <td nowrap="nowrap" class="first-hidden">${vh.format_date(disp_payment_date) if disp_payment_date else u'-'}</td>
        <td nowrap="nowrap" class="first-hidden">${vh.display_payment_shop_code(receipt)}</td>
        <td nowrap="nowrap" class="first-hidden">${vh.get_shop_name_text(vh.get_famiport_shop_by_code(payment_shop_code)) if payment_shop_code != u'-' else u'-'}</td>

        <td nowrap="nowrap" class="first-hidden">${vh.format_date(disp_delivery_date) if disp_delivery_date else u'-'}</td>
        <td nowrap="nowrap" class="first-hidden">${vh.display_delivery_shop_code(receipt)}</td>
        <td nowrap="nowrap" class="first-hidden">${vh.get_shop_name_text(vh.get_famiport_shop_by_code(delivery_shop_code)) if delivery_shop_code != u'-' else u'-'}</td>
      </tr>
    % endfor
    </tbody>
  </table>
  % else:
    <p>検索条件にマッチする申込はありません</p>
  % endif
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
        $('#completed_from').datepicker({
              format: "yyyy-mm-dd",
              language: "ja",
              autoclose: true
            });
        $('#completed_to').datepicker({
              format: "yyyy-mm-dd",
              language: "ja",
              autoclose: true
        });
        $('.toggle-btn').on('click', function(e) {
            e.preventDefault();
            console.log('push toggle');
            $('td.first-hidden, th.first-hidden').show();
        });
        $('.reset-btn').click(function() {
            $('.search-table input').attr('value', '');
        });
      });
</script>

