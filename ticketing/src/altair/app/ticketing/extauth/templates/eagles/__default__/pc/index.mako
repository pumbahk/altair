<%inherit file="base.mako" />
<% member_set = _context.member_sets[0] %>
<h2>ログイン方法の選択</h2>

<div class="loginBox2 clearfix">


<!-- guest LOGIN BOX -->
<div class="user-guest tileLogin">
<form action="${_context.route_path('extauth.login')}" method="POST">
<dl>
% for member_kind in member_set.member_kinds:
% if member_kind.show_in_landing_page and member_kind.enable_guests:
<dt class="user-guest-name"><span>${member_kind.name}の方</span>はこちらから</dt>
<dd>
<p><button class="btnL" name="doGuestLoginAs${member_kind.name}" style="margin-top: 70px;">チケット購入</button></p>
</dd>
% endif
% endfor
</dl>
<input type="hidden" name="member_set" value="${member_set.name}" />
<input type="hidden" name="_" value="${request.session.get_csrf_token()}" />
</form>
</div>

<!-- member LOGIN BOX -->
<div class="user-member tileLogin">
<dl>
<dt class="user-member-name"><span>ファンクラブの方</span>はこちらから</dt>
<dd>

<ul class="fcType">
<li style="background:#333;">ブースタークラブ</li>
<li style="background:#d6a200">ゴールドクラブ</li>
<li style="background:#aaa;">レギュラークラブ</li>
<li style="background:#d65a8f;">レディースクラブ</li>
<li style="background:#65aa00;">キッズクラブ</li>
<li style="background:#00A0E9;">E25クラブ</li>
<li style="background:#7D001A;">ベーシッククラブ</li>
<li style="background:#002D54;">スポンサークラブ</li>
<li style="background:#00FF00;">スクール</li>
<li style="background:#ffa500;">SOC</li>
<li style="background:#000000;">ろっけんイーグルス</li>
</ul>

<p class="tac mgt20"><a href="${_context.route_path('extauth.rakuten.entry')}" class="btnL">ログイン</a></p>
<p class="mgt20">※会員ID・パスワードを忘れてしまった方は<a href="https://eagles.tstar.jp/idpw" target="_blank">こちら</a></p>
</form>
</dd>
</dl>
</div>

<!-- stockholder LOGIN BOX -->
<div class="btn-stockholder">
<p class="tac"><a href="${_context.route_path('extauth.login', _query=dict(member_set=member_set.name))}" class="btnSH"><span>株主優待の方はこちらから</span></a></p>
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
