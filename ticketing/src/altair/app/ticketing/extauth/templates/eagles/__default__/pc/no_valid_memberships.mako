<%inherit file="base.mako" />

    <div class="login-fan-public-page">
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
            <div class="attention-wrap">
              <div class="inner">
                <p>ご入力いただいた楽天IDはファンクラブ会員IDと連携していない楽天IDです。<br>一般（非ファンクラブ会員）の方は「次へ進む」からお進みください。</p>
              </div>
            </div>
            <table class="login-tbl">
              <tr>
                <td class="login-box login-fanclub">
                  <h3 class="sub-ttl">ファンクラブに入会済み</h3>
                  <div class="btn-box">
<%!
from datetime import datetime
thisyear = datetime.now().strftime('%Y')
%>
                    <a href="https://eagles.fanclub.rakuten.co.jp/mypage/login/ridLogin" class="btn btn-primary">
                      <span>楽天IDを連携する</span>
                    </a>
                  </div>

                  <a href="//www.rakuteneagles.jp/fanclub/" class="login-link">ファンクラブに入会をご希望の方はこちらから</a>

                </td>
                <td class="login-box login-public">
                  <h3 class="sub-ttl">一般の方</h3>
                  <div class="btn-box">
                    <a href="${_context.route_path('extauth.authorize', _query=dict(_=request.session.get_csrf_token(), use_fanclub=False))}" class="btn btn-primary">
                      <span>次へ進む</span>
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
                <p class="info-txt">楽天野球団チケットセンター<br>TEL:050-5817-8192（10:00〜18:00）※不定休</p>
              </li>
            </ul>
          </div>
        </section>
      </div>
      <!-- .contents -->
    </div>
    <!-- .login-fan-public-page -->

<!--SiteCatalyst-->
<%
    sc = {"pagename": "no-valid-user"}
%>
<%include file="../common/sc_basic.html" args="sc=sc" />
<!--/SiteCatalyst-->
