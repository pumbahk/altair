<%inherit file="/_base.mako" />
<h1>払戻受付</h1>
<form action="${request.current_route_path()}" method="POST">
<fieldset>
  <legend>バーコード番号</legend>
  % for i, barcode_no in enumerate(barcode_no_list):
    <label>バーコード番号${i + 1}</label>
    <input type="text" placeholder="バーコード番号" name="barcode_no" maxlength="13" value="${barcode_no}" />
  % endfor
  <button type="submit" class="btn">確認</button>
</form>
