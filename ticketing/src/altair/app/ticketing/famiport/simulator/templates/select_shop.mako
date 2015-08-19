<%inherit file="/_base.mako" />
<h1>ショップコード / MMK入力</h1>
<form action="${request.current_route_path()}" method="POST">
<fieldset>
  <label></label>
  <input type="text" placeholder="ショップコード" name="store_code" maxlength="5" value="${store_code}" />
  <input type="text" placeholder="発券Famiポート番号" name="mmk_no" maxlength="1" value="${mmk_no}" />
  <input type="hidden" value="${return_url}" />
  <input type="submit" class="btn" />
</form>
