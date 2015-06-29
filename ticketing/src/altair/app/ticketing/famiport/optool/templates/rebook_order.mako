<%inherit file="_base.mako"/>
<div class="jumbotron">
  <form class="form re_order_form">
    <div class="row" style="margin-bottom:10px;">
      <h3 class="form-heading">発券方法</h3>
      <div class="form-group">
        <label class="radio-inline">
          <input type="radio" name="optradio"><span class="text-lg">同席番再予約</span>
        </label>
        <label class="radio-inline">
          <input type="radio" name="optradio"><span class="text-lg">再発券</span>
        </label>
      </div>
      <div class="form-group">
        <label for="sel1" class="col-md-2 control-label">理由コード:</label>
        <div class="col-md-10">
          <select class="form-control" id="sel1">
            <option>【910】同席番再予約（店舗都合）</option>
            <option>【911】同席番再予約（お客様都合）</option>
            <option>【912】同席番再予約（強制成立）</option>
            <option>【913】再発券（店舗都合）</option>
            <option>【914】その他</option>
          </select>
        </div>
      </div>
      <div class="form-group">
        <label for="reason_area" class="col-md-2 control-label">理由備考:</label>
        <div class="col-md-10">
          <textarea class="form-control" rows="3" id="reason_area"></textarea>
        </div>
      </div>
      <div class="form-group">
          <label for="old_num_type" class="col-md-2">旧番号種類:</label>
          <div class="col-md-10">
            <input type="text" class="form-control" id="old_num_type" value="払込票番号">
          </div>
      </div>
      <div class="form-group">
          <label for="old_num" class="col-md-2">旧番号:</label>
          <div class="col-md-10">
            <input type="text" class="form-control" id="old_num" value=${receipt.barcode_no}>
          </div>
      </div>
    </div>
    <div class="row pull-right">
      <button type="submit" class="btn btn-default">理由修正</button>
      <button type="button" class="btn btn-default" data-toggle="modal" data-target="#myModal">実行</button>
      <a href="search.html"><button type="button" class="btn btn-default">閉じる</button></a>
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
  $("#modal_ok").on('click', function() {
    $('.modal-title').html('実行結果');
    $('.modal-body').html('正常に終了しました<br><br> 払込票番号が「1」から「2」に変わりました。');
  });
});
</script>
