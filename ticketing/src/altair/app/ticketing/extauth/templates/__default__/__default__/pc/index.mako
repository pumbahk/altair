<%inherit file="base.mako" />
<ul>
  <li><p><a href="${request.route_path('extauth.rakuten.entry', subtype=_context.subtype)}">楽天会員としてログイン</a></p></li>
  <li>
    <p>株主ログイン</p>
    <form>
      <label for="stockholder-username">ユーザ名</label>
      <input id="stockholder-username" type="text" name="username" />
      <label for="stockholder-password">パスワード</label>
      <input id="stockholder-password" type="password" name="password" />
    </form>
  </li>
</ul>
