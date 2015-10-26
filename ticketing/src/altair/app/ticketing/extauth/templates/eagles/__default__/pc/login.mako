<%inherit file="base.mako" />
<% member_set = selected_member_set %>
<h2>イーグルスチケット各種優待会員ログイン</h2>

<div class="loginBox2 clearfix">


<!-- member LOGIN BOX -->
<div class="user-stockholder">
<dl>
<dt class="user-member-name"><span>各種会員IDをお持ちの方</span>はこちらから</dt>
<dd>

<ul class="fcType">
<li style="background:#a371ff;">株主優待</li>
<li style="background:#00FF00;">スクール</li>
<li style="background:#ffa500;">SOC</li>
<li style="background:#000000;">ろっけんイーグルス</li>
</ul>

<form action="${_context.route_path('extauth.login')}" method="POST">
<table class="loginTBL">
<tbody>
<tr>
<th>${h.auth_identifier_field_name(member_set)}</th>
<td>
  <input type="text" class="text" name="username" value="${username}" />
  % if message:
  <p>${message}</p>
  % endif
</td>
</tr>
<tr>
<th>${h.auth_secret_field_name(member_set)}</th>
<td><input type="password" name="password" value="${password}" /></td>
</tr>
</tbody>
</table>
<p class="tac"><input type="submit" class="btnL" value="ログイン"></p>
<input type="hidden" name="member_set" value="${selected_member_set.name}" />
<input type="hidden" name="_" value="${request.session.get_csrf_token()}" />
</form>
</dd>
</dl>
</div>

</div>



<h3>注意事項</h3>
<ul class="notes">
<li>会員の方も、受付番号（REから始まる12ケタ）から確認することができます。</li>
<li>会員ID・パスワードは半角でご入力ください。</li>
</ul>

<h3>お問い合わせ</h3>

<ul class="notes">
<li>楽天野球団チケットセンター：050-5817-8192(平日10時～18時)※不定休</li>
</ul>
