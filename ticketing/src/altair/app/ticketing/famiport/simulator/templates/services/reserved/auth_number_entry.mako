<%inherit file="/_base.mako" />
<h1>認証番号入力画面</h1>
<div>
  <form action="${request.current_route_path()}" method="POST">
    <fieldset>
      <input type="text" name="auth_number" placeholder="認証番号 (13桁)" value="${auth_number}" />
      <input type="submit" class="btn" />
    </fieldset>
  </form>
</div>
