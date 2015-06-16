<%inherit file="/_base.mako" />
<h1>予約番号入力画面</h1>
<div>
  <form action="${request.current_route_path()}" method="POST">
    <fieldset>
      <input type="text" name="reserve_number" maxlength="13" placeholder="予約番号 (13桁)" value="${reserve_number}" />
      <input type="submit" class="btn" />
    </fieldset>
  </form>
</div>
