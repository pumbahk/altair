<%inherit file="base.mako" />
<% member_set = _context.member_sets[0] %>
  <div class="login-page">
    <div class="contents">

      <div class="bread-box">
        <div class="inner">
          <ul class="bread-list-box">
            <li class="bread-list"><a href="/" class="bread-link">Eチケトップ</a></li>
            <li class="bread-list">ファンクラブ会員、一般選択</li>
          </ul>
        </div>
      </div>

      <section class="bg-contents">
        <div class="inner">
          <h2 class="page-ttl">ファンクラブ会員、一般選択</h2>

          <table class="login-tbl ">
            <tr>
              <td class="login-box login-fun js-sp-accotdion-btn">
                <h3 class="sub-ttl">ファンクラブ会員の方</h3>
                <div class="img-box"><img src="${view_context.static_url('images/culb-rank.png')}" alt="クラブ"></div>
                <div class="btn-box" style="font-size:10px;">※キッズクラブの方は＜一般の方＞からログインください</div>
                <div class="btn-box">
                  <a href="${_context.route_path('extauth.rakuten.entry')}" class="btn btn-eagles">
                    <img src="${view_context.static_url('images/logo_rakuten.jpg')}" class="logo" width="70px" alt="楽天">
                    <span>楽天会員IDでログイン</span>
                  </a>
                </div>
                <div class="btn-box">
<%! 
from datetime import datetime
thisyear = datetime.now().strftime('%Y')
%>
                  <a href="https://eagles.fanclub.rakuten.co.jp/mypage/login/ridLogin" class="btn btn-normal">
                    <span class="txt">楽天会員ID連携がお済でない方はこちら</span><br><span class="caution">※ファンクラブ会員と連携した楽天会員ID・パスワードが必要です。</span>
                  </a>
                </div>
                <a href="https://member.id.rakuten.co.jp/rms/nid/upkfwd" target="_blank" class="login-link">会員ID・パスワードを忘れてしまった方はこちら</a>
                <div class="btn-box">
                  <a href="${_context.route_path('extauth.login', _query=dict(member_set=member_set.name))}" class="btn btn-has-ohter-id">その他会員IDをお持ちの方はこちら<br>Sign in with other ID</a>
                </div>
                <div class="page-top-box js-show-box">
                  <a href="#" class="sp page-top">
                    <span class="arrow top"></span>
                  </a>
                </div>
              </td>
              <td class="login-box login-normal js-sp-accotdion-btn">
                <h3 class="sub-ttl">一般の方</h3>
                <div class="btn-box for-general">
                  <a href="${_context.route_path('extauth.rakuten.entry', _query=dict(use_fanclub=False))}" class="btn btn-eagles">
                    <img src="${view_context.static_url('images/logo_rakuten.jpg')}" class="logo" width="70px" alt="楽天">
                    <span>楽天会員IDでログイン</span>
                  </a>
                </div>
                <div class="btn-box">
                  <a href="https://grp03.id.rakuten.co.jp/rms/nid/registfwdi?openid.return_to=https%3A%2F%2Feagles.tstar.jp&service_id=e17&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.oauth.consumer=e_tkt&openid.mode=checkid_setup&internal.id.mode=auth&openid.oauth.scope=rakutenid_basicinfo%2Crakutenid_contactinfo%2Crakutenid_pointaccount&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns.oauth=http%3A%2F%2Fspecs.openid.net%2Fextenstions%2Foauth%2F1.0" class="btn btn-normal">
                    <span class="txt">楽天会員に新規登録（無料）<br>してサービスを利用する</span>
                  </a>
                </div>
                <div class="page-top-box js-show-box">
                  <a href="#" class="sp page-top">
                    <span class="arrow top"></span>
                  </a>
                </div>
              </td>
            </tr>
          </table>
        </div>
      </section>

      <section class="info-box">
        <div class="inner">
          <ul class="info-list-box">
            <li class="info-list">
              <h3 class="sub-ttl">注意事項</h3>
              <p class="info-txt">■会員の方も、受付番号（REから始まる12ケタ）から確認することができます。<br>■会員ID・パスワードは半角でご入力ください。</p>
            </li>
            <li class="info-list">
              <h3 class="sub-ttl">お問い合わせ</h3>
              <p class="info-txt">楽天野球団チケットセンター<br>TEL:050-5817-8192（10:00〜18:00）</p>
            </li>
          </ul>
        </div>
      </section>
    </div>
  </div>
    <!-- .contents -->

<!--SiteCatalyst-->
<%
    sc = {"pagename": "index" }
%>
<%include file="../common/sc_basic.html" args="sc=sc" />
<!--/SiteCatalyst-->
