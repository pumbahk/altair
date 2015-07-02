<%inherit file="_base.mako"/>
<div class="jumbotron">
  <form id="rebookform" class="form re_order_form" action="${request.route_url('rebook_order', action='rebook', receipt_id=receipt.id)}" method="post">
    <div class="row" style="margin-bottom:10px;">
      <h3 class="form-heading">発券方法</h3>
      <div class="form-group">
        <label class="radio-inline">
          <input type="radio" name="optradio" value="rebook" checked="checked"><span class="text-lg">同席番再予約</span>
        </label>
        <label class="radio-inline">
          <input type="radio" name="optradio" value="reprint"><span class="text-lg">再発券</span>
        </label>
      </div>
      <div class="form-group">
        <div class="col-md-2">${form.reason_code.label}</div>
        <div class="col-md-10">${form.reason_code(class_="form-control")}</div>
      </div>
      <div class="form-group">
        <div class="col-md-2">${form.reason_text.label}</div>
        <div class="col-md-10">${form.reason_text(class_="form-control")}</div>
      </div>
      <div class="form-group">
          <div class="col-md-2">${form.old_num_type.label}</div>
          <div class="col-md-10">${form.old_num_type(class_="form-control", value=u"管理番号", readonly="readonly")}</div>
      </div>
      <div class="form-group">
          <div class="col-md-2">${form.old_num.label}</div>
          <div class="col-md-10">${form.old_num(class_="form-control", value=receipt.famiport_order_identifier, readonly="readonly")}</div>
      </div>
    </div>
    <div class="row pull-right">
      <button type="button" class="btn btn-default">理由修正</button>
      % if receipt.is_rebookable(now):
        <button type="button" class="btn btn-default" data-toggle="modal" data-target="#myModal">実行</button>
      % else:
        <span class="small">当予約は同席番再予約できません</span>
      % endif
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
      <div id="result-msg"></div>
      実行してもよろしいですか
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
        console.log('the button was pushed!');
        var $form = $("#rebookform");
        var $button = $("#modal_ok");
        $.ajax({
            url: $form.attr('action'),
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
                $('#result-msg').html('正常に終了しました');
                $('.modal-body').html($('input#old_num_type').val() + 'が「' + result['old_identifier'] + '」から「' + result['new_identifier'] + '」に変更されました');
            },
            error: function(xhr, textStatus, error) {
                $('#myModalLabel').html('実行結果');
                $('#result-msg').html('エラー');
                $('.modal-body').html('指定された申込は、同席番再予約ができません');
                console.log(error);
            }
        });
  });
  $("*[name=optradio]:radio").change(function(){
        var action = $(this).val();
        $("#rebookinfo").attr(
                    "href",
                    '${request.route_url('rebook_order', action='{action}', receipt_id='{receipt_id}')}'
                    .replace(encodeURIComponent('{action}'), action)
                    .replace(encodeURIComponent('{receipt_id}'), ${receipt.id})
                    );
    });
});
</script>
