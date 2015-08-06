<%inherit file="_base.mako"/>
<div class="jumbotron">
  <form id="rebookform" class="form re_order_form" action="${request.route_url('rebook_order', action='rebook', receipt_id=receipt.id)}" method="post">
    <div class="row" style="margin-bottom:10px;">
      <h3 class="form-heading">発券方法</h3>
      %if receipt.canceled_at is None:
      <div class="form-group">
        <label class="radio-inline">
          <input type="radio" name="optradio" value="rebook" checked="checked"><span class="text-lg">同席番再予約</span>
        </label>
        % if receipt.famiport_order.type == 4:
          <span class="small" style="color:red;">当予約は前払いのみのため、再発券出来ません</span>
        % else:
        <label class="radio-inline">
          <input type="radio" name="optradio" value="reprint"><span class="text-lg">再発券</span>
        </label>
        % endif
      </div>
      %endif
      <div class="form-group">
        <div class="col-md-2">${form.cancel_reason_code.label}</div>
        <div class="col-md-10">${form.cancel_reason_code(class_="form-control")}</div>
      </div>
      <div class="form-group">
        <div class="col-md-2">${form.cancel_reason_text.label}</div>
        <div class="col-md-10">${form.cancel_reason_text(class_="form-control")}</div>
      </div>
      <div class="form-group">
          <div class="col-md-2">${form.old_num_type.label}</div>
          <div class="col-md-10">${form.old_num_type(class_="form-control", value=u"管理番号", readonly="readonly")}</div>
      </div>
      <div class="form-group">
          <div class="col-md-2">${form.old_num.label}</div>
          <div class="col-md-10">${form.old_num(class_="form-control", value=vh.get_management_number_from_famiport_order_identifier(receipt.famiport_order_identifier), readonly="readonly")}</div>
      </div>
    </div>
    <div class="row pull-right">
      %if receipt.canceled_at is None:
        <button id="exe-button" type="button" class="btn btn-default" data-toggle="modal" data-target="#myModal">実行</button>
      %else:
        <button id="fix-reason" type="button" class="btn btn-default">理由修正</button>
        <span class="small">当予約はキャンセル済みのため再予約・再発券できません</span>
      %endif
    </div>
  </form>
</div>

<!-- Modal -->
<div class="modal fade" id="myModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">
<div class="modal-dialog" role="document">
  <div class="modal-content">
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
      <h4 class="modal-title" id="myModalLabel">確認</h4>
    </div>
    <div class="modal-body text-center">
      <div id="mbody-title"></div>
      <div id="mbody-msg">実行してもよろしいですか</div>
    </div>
    <div class="modal-footer">
      <button type="button" class="btn btn-primary" id="modal_ok">OK</button>
      <button type="button" class="btn btn-default" data-dismiss="modal">キャンセル</button>
    </div>
  </div>
</div>
</div>

<script type="text/javascript">
$(document).ready(function() {
    $("#modal_ok").on('click', function(e) {
        console.log($('#result-msg'));
        var $form = $("#rebookform");
        var $button = $("#modal_ok");
        var $url = $form.attr('action');
        $.ajax({
            url: $url,
            type: $form.attr('method'),
            data: $form.serialize(),
            timeout: 10000,

            // ２度押し防止
            beforeSend: function(xhr, settings) {
                $button.attr('disabled', true);
            },
            complete: function(xhr, textStatus) {
                $button.attr('disabled', false);
                $('#myModalLabel').html('実行結果');
                $('.modal-footer button').hide();
            },

            success: function(result, textStatus, xhr) {
                var $action = $("input[type='radio']:checked").val();
                if(result['error']) {
                    $('#mbody-title').html('エラー');
                    $('#mbody-msg').html('<span style="color:red;">' + result['error'] + '</span>');
                } else if ($action==='rebook') {
                    $('#mbody-title').html('正常に終了しました');
                    $('#mbody-msg').html($('input#old_num_type').val() + 'が「' + result['old_identifier'] + '」から「' + result['new_identifier'] + '」に変更されました');
                } else if ($action==='reprint') {
                    $('#mbody-title').html('正常に終了しました');
                    $('#mbody-msg').html('当予約のステータスを発券可能状態にしました');
                }
            },
            error: function(xhr, textStatus, error) {
                $('#mbody-title').html('エラー');
                $('#mbody-msg').html('処理に失敗しました');
                console.log(error);
            }
        });
    });
    $("#myModal").on("hidden.bs.modal", function(e) {
        console.log("modal closed!");
        $('#myModalLabel').html('確認');
        $('#mbody-title').html('');
        $('#mbody-msg').html('実行してもよろしいですか');
        $('.modal-footer button').show();
    });
    $("#fix-reason").on('click', function() {
        $("#rebookform").attr('action', '${request.route_url('rebook_order', action='fix-reason', receipt_id=receipt.id)}').submit();
    });
    $("*[name=optradio]:radio").change(function(){
        var action = $(this).val();
        $("#rebookform").attr(
                    "action",
                    '${request.route_url('rebook_order', action='{action}', receipt_id='{receipt_id}')}'
                    .replace(encodeURIComponent('{action}'), action)
                    .replace(encodeURIComponent('{receipt_id}'), ${receipt.id})
                    );
    });
});
</script>
