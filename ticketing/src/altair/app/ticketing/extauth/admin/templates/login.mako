<%inherit file="/base.mako" />
<h2>ログイン</h2>
<form id="login-form" method="POST">
  <ul>
  % for msg in request.session.pop_flash():
    <li>${msg}</li>
  % endfor
  </ul>
  <div class="control-group">
    <label class="control-label" for="login-form--user_name">ユーザ名</label>
    <div class="controls">
      ${form.user_name(id="login-form--user_name")}
    </div>
  </div>
  <div class="control-group">
    <label class="control-label" for="login-form--password">パスワード</label>
    <div class="controls">
      ${form.password(id="login-form--password")}
    </div>
  </div>
  <button class="btn">ログイン</button>
</form>
