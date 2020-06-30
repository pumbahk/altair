<%inherit file="base.mako" />

<section class="main loginArea">
<dl>
<dt>楽天会員の方はこちら</dt>
<dd><a href="${_context.route_path('extauth.rakuten.entry')}" class="btnLogin"><span class="login-fc-btn">楽天IDでログイン</span></a></dd>
<dd><a href="" class="btnID">楽天会員に登録する</a></dd>
<dd>
<ul>
<li>※楽天IDでログインいただくと、2回目以降のお客様情報のご入力がスムーズになります。</li>
<li>※ポイントの付与期間は、施設によって異なります。</li>
</ul>
</dd>
</dl>
</section><!-- /loginArea -->
