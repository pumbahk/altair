<%inherit file="base.mako" />
<% member_set = _context.member_sets[0] %>
<p class="box bold tac fs18" style="color: red;">2016年ファンクラブ会員先行購入は楽天会員IDと連携済のお客様のみが対象となります。</p>


<div class="box clearfix">


<!-- member LOGIN BOX -->
<div class="col2_1 tile2 login-box">
<dl>
<dt class="login-name" id="rakulogintitle"><span>ファンクラブの方</span>はこちらから</dt>
<dd class="login-inbox" id="rakulogin">

<ul class="fcType clearfix">
<li class="fcType-L" style="background:#D3D1D0;"><img src="${view_context.static_url('images/status_booster.png')}" alt="ブースタークラブ"></li>
<li class="fcType-L" style="background:#FDEECC"><img src="${view_context.static_url('images/status_gold.png')}" alt="ゴールドクラブ"></li>
<li class="fcType-L" style="background:#E7E7E7;"><img src="${view_context.static_url('images/status_regular.png')}" alt="レギュラークラブ"></li>
<li class="fcType-L" style="background:#FAD5E8;"><img src="${view_context.static_url('images/status_ladies.png')}" alt="レディースクラブ"></li>
<li class="fcType-L" style="background:#CCECFA;"><img src="${view_context.static_url('images/status_e25.png')}" alt="E25クラブ"></li>
<li class="fcType-L" style="background:#E5CCD1;"><img src="${view_context.static_url('images/status_basic.png')}" alt="ベーシッククラブ"></li>
<li class="fcType-L" style="background:#EFEFEF;"><img src="${view_context.static_url('images/status_rocken.png')}" alt="ろっけんイーグルス"></li>
</ul>
<p class="tac mgt20 mgb10"><a href="${_context.route_path('extauth.rakuten.entry')}" class="btnA btnA_l"><span class="login-fc-btn">楽天会員IDでログイン</span></a></p>
<p class="fs12" style="color: red;">※ファンクラブ会員と連携した楽天会員ID・パスワードが必要です。</p>
<p>※会員ID・パスワードを忘れてしまった方は<a href="https://eagles.tstar.jp/idpw" target="_blank">こちら</a></p>
<p class="tac mgt20"><a href="#" class="btnID">楽天会員ID連携がお済でない方はコチラ</a></p>
</dd>
</dl>
</div>

<!-- guest LOGIN BOX -->
<div class="col2_2 tile2 login-box">
<form action="${_context.route_path('extauth.login')}" method="POST">
<dl>
% for member_kind in member_set.member_kinds:
% if member_kind.show_in_landing_page and member_kind.enable_guests:
<dt class="login-name" id="guestlogintitle"><span>${member_kind.display_name}の方</span>はこちらから</dt>
<dd class="login-inbox" id="guestlogin">
<p><button class="btnA btnA_l login-guest-btn" name="doGuestLoginAs${member_kind.name}">次へ進む</button></p>
</dd>
% endif
% endfor
</dl>
<input type="hidden" name="member_set" value="${member_set.name}" />
<input type="hidden" name="_" value="${request.session.get_csrf_token()}" />
</form>
</div>



<!-- stockholder LOGIN BOX -->
<div class="btn-stockholder">
<p class="clear tar pdt10 pdr20">&raquo; <a href="${_context.route_path('extauth.login', _query=dict(member_set=member_set.name))}"><span>その他会員の方はコチラから</span></a></p>
</div>

</div>


<article class="box">
<h3 class="heading-bline">注意事項</h3>
<ul class="list-disc">
<li>会員の方も、受付番号（REから始まる12ケタ）から確認することができます。</li>
<li>会員ID・パスワードは半角でご入力ください。</li>
</ul>
</article>


<article class="box">
<h3 class="heading-bline">お問い合わせ</h3>
<ul class="list-disc">
<li>楽天野球団チケットセンター<br>
TEL: 050-5817-8192（平日10時～18時）※不定休</li>
</ul>
</article>
