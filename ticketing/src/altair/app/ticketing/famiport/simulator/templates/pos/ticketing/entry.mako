<%inherit file="/_base.mako" />
<h1>引換票・払込票番号入力</h1>
<form action="${request.current_route_path()}" method="POST">
<fieldset>
  <label>引換票番号</label>
  <input type="text" placeholder="引換票番号" name="barcode_no" maxlength="13" value="${barcode_no}" />
  <input type="submit" class="btn" />
</form>

