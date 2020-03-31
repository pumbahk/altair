<%inherit file="base.mako" />
<% member_set = _context.member_sets[0] %>
<%!
   from datetime import datetime
   thisyear = datetime.now().strftime('%Y')
%>
<section class="main login">
  <div class="wrap">
    <h2 align="center">${_(u'会員選択')}</h2>
      <p class="lead"><span>${_(u'購入したチケットは、購入時に選択したログイン画面からのみ表示されます。')}</span><br>
          <span>${_(u'※異なるログイン画面からは表示されませんのでご注意ください。')}</span>
    </p>
    <div class="boxArea clearfix">
      <table width="100%">
        <tr>
          <td>
            <!-- member loginbox -->
            <div class="box login-box">
              <dl>
                <dt class="login-name" id="rakulogintitle"><span>${_(u'ファンクラブ会員の方')}</span></dt>
                <dd class="login-inbox" id="rakulogin">
                  <div class="img-box"><img src="${view_context.static_url('images/vissel-rank.png')}" alt="クラブランク"></div>
                  <p><a href="${_context.route_path('extauth.rakuten.entry')}" class="btnA"><span class="login-fc-btn">${_(u'楽天IDでログイン')}</span></a></p>
                  <p><a href="https://vissel.fanclub.rakuten.co.jp/mypage/login" class="btnID" target="_blank">${_(u'楽天ID連携がお済でない方はこちら')}</a></p>
                </dd>
              </dl>
            </div>
          </td>
        </tr>

        <tr>
          <td>
            <!-- guest loginbox -->
            <div class="box login-box">
              <dl>
                <dt class="login-name" id="guestlogintitle"><span>${_(u'一般の方')}</span></dt>
                <dd class="login-inbox" id="guestlogin">
                  <p class="rakuten-login-button"><a href="${_context.route_path('extauth.rakuten.entry', _query=dict(use_fanclub=False))}" class="btnA btnA_l"><span class="login-fc-btn">${_(u'楽天IDでログイン')}</span></a></p>
                  <p><a href="https://grp03.id.rakuten.co.jp/rms/nid/registfwdi?openid.return_to=https%3A%2F%2Fvissel.tstar.jp&service_id=e27&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.oauth.consumer=vissel_tkt&openid.mode=checkid_setup&internal.id.mode=auth&openid.oauth.scope=rakutenid_basicinfo%2Crakutenid_contactinfo%2Crakutenid_pointaccount&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns.oauth=http%3A%2F%2Fspecs.openid.net%2Fextenstions%2Foauth%2F1.0" class="btnID" target="_blank">${_(u'楽天会員に新規登録(無料)してサービスを利用する')}</a></p>
                </dd>
              </dl>
            </div>
          </td>
        </tr>

        <tr>
          <td>
            <!-- annual seat loginbox -->
            <div class="box login-box">
              <dl>
                <dt class="login-name" id="annuallogintitle"><span>${_(u'【法人】年間シートオーナーの方')}</span></dt>
                <dd class="login-inbox" id="annuallogin">
                  <p class="rakuten-login-button"><a href="${_context.route_path('extauth.login', _query=dict(member_set=member_set.name))}" class="btnA btnA_l"><span class="btn">${_(u'ログイン')}</span></a></p>
                </dd>
              </dl>
            </div>
          </td>
        </tr>

        <tr>
          <td>
            <!-- other members loginbox -->
            <div class="box login-box">
              <dl>
                <dt class="login-name" id="otherlogintitle"><span>${_(u'その他会員の方')}</span></dt>
                <dd class="login-inbox" id="otherlogin">
                  <p class="rakuten-login-button"><a href="${_context.route_path('extauth.login', _query=dict(member_set=member_set.name))}" class="btnA btnA_l"><span class="btn">${_(u'ログイン')}</span></a></p>
                </dd>
              </dl>
            </div>
          </td>
        </tr>
        <tr>
          <td>
            <div class="login-inbox">
              <dd class="login-inbox">
                  <p class="order-no-login-text">${_(u'受付番号からの購入履歴確認は{}こちら{}から').format('<a href="https://vissel.tstar.jp/orderreview/form">', '</a>')|n}</p>
              </dd>
            </div>
          </td>
        </tr>
      </table>
    </div>
  </div><!-- /wrap -->
<!-- back to top--><div id="topButton"><a>▲<br>${_(u'上へ')}</a></div><!-- /back to top-->
</section><!-- /main -->

<!--SiteCatalyst-->
<%
    sc = {"pagename": "index"}
%>
<%include file="../common/sc_basic.html" args="sc=sc" />
<!--/SiteCatalyst-->
