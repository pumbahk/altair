<%inherit file="base.mako" />

<section class="main loginArea">
<dl>
<dt>楽天会員の方はこちら</dt>
<dd><a href="${_context.route_path('extauth.rakuten.entry')}" class="btnLogin"><span class="login-fc-btn">楽天会員IDでログイン</span></a></dd>
<dd><a href="" class="btnID">楽天会員に登録する</a></dd>
<dd>
<ul>
<li>※楽天会員IDでログインいただくと、2回目以降のお客様情報のご入力がスムーズになります。</li>
<li>※楽天スーパーポイント口座をご用意ください。</li>
<li>※ポイントの付与期間は、施設によって異なります。</li>
</ul>
</dd>
</dl>
<dl>
<dt>一般の方はこちら</dt>
<dd>
<form action="${_context.route_path('extauth.login',_query=request.GET)}" method="POST">
<input type="submit" name="doGuestLoginAsGuest" class="btnLogin" value="購入する"></dd>
<input type="hidden" name="member_set" value="leisure"></dd>
<input type="hidden" name="_" value="${request.session.get_csrf_token()}" />
</form>
<dd class="no-sp"></dd>
<dd>
<ul>
<li>※楽天スーパーポイント口座をご用意ください。</li>
<li>※ポイントの付与期間は、施設によって異なります。</li>
<li>※楽天会員でご購入いただくことをお勧めします。</li>
</ul>
</dd>
</dl>
</section><!-- /loginArea -->
