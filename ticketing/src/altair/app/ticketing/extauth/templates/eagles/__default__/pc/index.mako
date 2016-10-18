<%inherit file="base.mako" />
<% member_set = _context.member_sets[0] %>
<p class="box bold tac fs18" style="color: red;">イーグルスチケットでのチケットのお求めには楽天会員IDが必要になりました。<br>楽天会員IDをお持ちでないお客様は会員登録をお願いします。</p>

<div class="box clearfix">
<!-- member LOGIN BOX -->
<div class="col2_1 tile2 login-box">
<dl>
<dt class="login-name" id="rakulogintitle"><span>ファンクラブ会員の方</span></dt>
<dd class="login-inbox" id="rakulogin">

<ul class="fcType clearfix">
<li class="fcType-L" style="background:#D3D1D0;"><img src="${view_context.static_url('images/status_booster.png')}" alt="ブースタークラブ"></li>
<li class="fcType-L" style="background:#FDEECC;"><img src="${view_context.static_url('images/status_gold.png')}" alt="ゴールドクラブ"></li>
<li class="fcType-L" style="background:#E7E7E7;"><img src="${view_context.static_url('images/status_regular.png')}" alt="レギュラークラブ"></li>
<li class="fcType-L" style="background:#FAD5E8;"><img src="${view_context.static_url('images/status_ladies.png')}" alt="レディースクラブ"></li>
<li class="fcType-L" style="background:#CCECFA;"><img src="${view_context.static_url('images/status_e25.png')}" alt="E25クラブ"></li>
<li class="fcType-L" style="background:#E5CCD1;"><img src="${view_context.static_url('images/status_basic.png')}" alt="ベーシッククラブ"></li>
<li class="fcType-L" style="background:#EFEFEF;"><img src="${view_context.static_url('images/status_rocken.png')}" alt="ろっけんイーグルス"></li>
</ul>
<p class="tac mgt20 mgb10"><a href="${_context.route_path('extauth.rakuten.entry')}" class="btnA btnA_l"><span class="login-fc-btn">楽天会員IDでログイン</span></a></p>
<%! 
from datetime import datetime
thisyear = datetime.now().strftime('%Y')
%>
<p class="tac mgt20"><a href="https://eagles.fanclub.rakuten.co.jp/mypage/login/ridLogin?year=${thisyear}" class="btnID">楽天会員ID連携がお済でない方はこちら</a></p>
<p class="fs12" style="color: red;">※ファンクラブ会員と連携した楽天会員ID・パスワードが必要です。</p>
<p>※会員ID・パスワードを忘れてしまった方は<a href="https://member.id.rakuten.co.jp/rms/nid/upkfwd" target="_blank">こちら</a></p>
<!-- stockholder LOGIN BOX -->
<div class="btn-stockholder">
<p class="clear tar pdt10 pdr20">&raquo; <a href="${_context.route_path('extauth.login', _query=dict(member_set=member_set.name))}"><span>その他会員の方はこちらから</span></a></p>
</div>
</dd>
</dl>
</div>

<!-- guest LOGIN BOX -->
<div class="col2_2 tile2 login-box">
<dl>
<dt class="login-name" id="guestlogintitle"><span>一般の方</span></dt>
<dd class="login-inbox" id="guestlogin">
<p class="tac rakuten-login-button"><a href="${_context.route_path('extauth.rakuten.entry', _query=dict(use_fanclub=False))}" class="btnA btnA_l"><span class="login-fc-btn">楽天会員IDでログイン</span></a></p>
<p class="tac mgt20"><a href="https://grp03.id.rakuten.co.jp/rms/nid/registfwdi?openid.return_to=https%3A%2F%2Feagles.tstar.jp&service_id=e17&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.oauth.consumer=e_tkt&openid.mode=checkid_setup&internal.id.mode=auth&openid.oauth.scope=rakutenid_basicinfo%2Crakutenid_contactinfo%2Crakutenid_pointaccount&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns.oauth=http%3A%2F%2Fspecs.openid.net%2Fextenstions%2Foauth%2F1.0" class="btnID" target="_blank">楽天会員に新規登録(無料)してサービスを利用する</a></p>
</dd>
</dl>
</div>
</div>


<article class="box">
<h3 class="heading-bline">注意事項</h3>
<ul class="list-disc">
<li>会員ID・パスワードは半角でご入力ください。</li>
<li>購入履歴の確認は、会員の方も、受付番号（REから始まる12ケタ）から確認することができます。</li>
</ul>
</article>


<article class="box">
<h3 class="heading-bline">お問い合わせ</h3>
<ul class="list-disc">
<li>楽天野球団チケットセンター<br>
TEL: 050-5817-8192（10時～18時）※不定休</li>
</ul>
</article>

<!--SiteCatalyst-->
<%
    sc = {"pagename": "index" }
%>
<%include file="../common/sc_basic.html" args="sc=sc" />
<!--/SiteCatalyst-->
