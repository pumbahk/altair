<%inherit file="/_base.mako" />
<h1>ショップコード入力</h1>
<form action="${request.current_route_path()}" method="POST">
<fieldset>
  <label></label>
  <input type="text" placeholder="ショップコード" name="store_code" maxlength="5" value="${store_code}" />
  <input type="hidden" value="${return_url}" />
</form>
