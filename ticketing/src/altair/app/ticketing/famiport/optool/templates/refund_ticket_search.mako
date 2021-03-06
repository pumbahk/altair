<%inherit file="_base.mako"/>
<div class="jumbotron">
<form class="form" id="search-form" action="" method="get">
  <div class="row">
    <div class="col-md-10">
      <h3 class="form-heading">払戻チケットデータ検索</h3>
      <table class="search-table">
        <thead><tr><th colspan="4">払戻対象公演</th></tr></thead>
        <tbody>
        <tr>
          <td colspan="3" nowrap="nowrap">
            <div class="form-group">
              <label class="radio-inline">
                ${form.before_refund}${form.before_refund.label}
              </label>
              <label class="radio-inline">
                ${form.during_refund}${form.during_refund.label}
              </label>
              <label class="radio-inline">
                ${form.after_refund}${form.after_refund.label}
              </label>
            </div>
          </td>
        </tr>
        </tbody>
        <thead><tr><th colspan="4">チケット情報</th></tr></thead>
        <tbody>
        <tr>
            <th class="pull-right">${form.management_number.label}</th>
            <td>${form.management_number}</td>
            <th class="pull-right">${form.barcode_number.label}</th>
            <td>${form.barcode_number}</td>
        </tr>
        <tr>
            <th class="pull-right" nowrap="nowrap">${form.event_code.label}</th>
            <td>${form.event_code}</td>
            <th class="pull-right" nowrap="nowrap">${form.event_subcode.label}</th>
            <td>${form.event_subcode}</td>
        </tr>
        <tr>
            <th class="pull-right" nowrap="nowrap">${form.refunded_shop_code.label}</th>
            <td>${form.refunded_shop_code}</td>
            <th class="pull-right" nowrap="nowrap">${form.order_no.label}</th>
            <td>${form.order_no}</td>
        </tr>
        <tr>
            <th class="pull-right">${form.performance_start_date.label}</th>
            <td colspan="3">
                ${form.performance_start_date}
                ${form.performance_end_date.label}
                ${form.performance_end_date}
            </td>
        </tr>
        </tbody>
      </table>
    </div>

    <div class="buttonBox col-md-2">
      <button type="reset" class="btn btn-default reset-btn">クリア<span class="glyphicon glyphicon-erase"></span></button>
      <button type="submit" class="btn btn-lg btn-default">検索
        <span class="glyphicon glyphicon-search"></span>
      </button>
    </div>
  </div>
</form>
</div>
<div id="table-content">
  % if entries:
  <div class="row">
    <div class="col-md-3">
      <h4>払戻チケット一覧</h4>
    </div>
    <div class="col-md-9 text-center">
      <h4>検索結果件数${entries.item_count}件</h4>
    </div>
  </div>
  ${entries.pager(link_attr={"class": "btn small"}, curpage_attr={"class": "btn primary small disabled"})}
      <table class="table table-hover">
        <thead>
          <tr>
            <!-- <th nowrap="nowrap">選択</th> -->
            % for column in columns:
                <th nowrap="nowrap">${column[1]}</th>
            % endfor
          </tr>
        </thead>

        <tbody>
        % for entry in entries:
        <% famiport_refund_entry = entry.FamiPortRefundEntry %>
        <% famiport_receipt = entry.FamiPortReceipt %>
        <% famiport_shop = rts_helper.get_famiport_shop_by_code(famiport_refund_entry.shop_code) %>
        <tr>
            <!-- <td><input type="radio" value="1" name="radio_gr" form="order"></td> -->
            <td>${rts_helper.get_refund_status_text(famiport_refund_entry.refunded_at)}</td>
            <td>${famiport_shop.district_code if famiport_shop else '-'}</td>
            <td>${famiport_shop.branch_code if famiport_shop else '-'}</td>
            <% ticketing_shop_code = famiport_refund_entry.famiport_ticket.famiport_order.ticketing_famiport_receipt.shop_code%>
            <td>${ticketing_shop_code if ticketing_shop_code else '-'}</td>
            <td>${rts_helper.get_shop_name_text(rts_helper.get_famiport_shop_by_code(ticketing_shop_code))}</td>
            <td>${rts_helper.get_management_number_from_famiport_order_identifier(famiport_refund_entry.famiport_ticket.famiport_order.famiport_order_identifier)}</td>
            <td>${famiport_refund_entry.famiport_ticket.barcode_number}</td>
            <td>${famiport_receipt.famiport_order.famiport_performance.famiport_event.code_1}</td>
            <td>${famiport_receipt.famiport_order.famiport_performance.famiport_event.code_2}</td>
            <td>${rts_helper.format_datetime(famiport_refund_entry.famiport_ticket.famiport_order.performance_start_at)}</td>
            <td nowrap="nowrap">${famiport_receipt.famiport_order.famiport_performance.famiport_event.name_1}</td>
            <td>${rts_helper.format_currency(famiport_refund_entry.total_amount)}</td>
            <td>${rts_helper.format_datetime(famiport_refund_entry.refunded_at)}</td>
            <td>${famiport_refund_entry.shop_code if famiport_refund_entry.refunded_at else '-'}</td>
            <td>${rts_helper.get_shop_name_text(famiport_shop)}</td>
            <td>${famiport_refund_entry.famiport_ticket.famiport_order.order_no}</td>
            <td>${famiport_refund_entry.famiport_ticket.famiport_order.famiport_sales_segment.name if famiport_refund_entry.famiport_ticket.famiport_order.famiport_sales_segment else u'-'}</td>
            <td>${famiport_refund_entry.famiport_ticket.famiport_order.customer_name}</td>
        </tr>
        % endfor
        </tbody>
      </table>
  % else:
    <p>検索条件にマッチする払戻チケットデータはありません</p>
  % endif
</div>
<div class="buttonBoxBottom pull-right">
  <!-- <button type="submit" class="btn btn-info">払戻取消</button> -->
  <button type="button" id="csv-download" class="btn btn-info">CSVダウンロード</button>
</div>
  <!-- /container -->

  <!-- Modal -->
  <div class="modal fade" id="myModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
          <h4 class="modal-title" id="myModalLabel">確認</h4>
        </div>
        <div class="modal-body text-center">
          払戻取消を実行してもよろしいですか
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-primary" id="modal_ok">OK</button>
          <button type="button" class="btn btn-default" data-dismiss="modal">キャンセル</button>
        </div>
      </div>
    </div>
  </div>

<script src="${request.static_url('altair.app.ticketing.famiport.optool:static/js/bootstrap-datepicker.min.js')}"></script>
<script src="${request.static_url('altair.app.ticketing.famiport.optool:static/js/bootstrap-datepicker.ja.min.js')}"></script>
<script type="text/javascript">
      $(document).ready(function () {
            $('#datepicker1').datepicker({
              format: "yyyy-mm-dd",
              language: "ja",
              autoclose: true
            });
            $('#datepicker2').datepicker({
              format: "yyyy-mm-dd",
              language: "ja",
              autoclose: true
            });
            $("#modal_ok").on('click', function() {
              $('.modal-title').html('実行結果');
              $('.modal-body').html('払戻取消は正常に行われました');
              $('.modal-footer').html('<button type="button" class="btn btn-default" data-dismiss="modal">閉じる</button>');
            });
            $("#csv-download").on('click', function() {
                $("#search-form").attr('action', '${request.route_url('download.refund_ticket')}').submit();
            });
            $('.reset-btn').click(function() {
                $('.search-table input').attr('value', '');
                $('.search-table :checkbox').attr('checked', false);
            });
      });
</script>
