<%inherit file="base.mako" />
<% member_set = selected_member_set %>
  <div class="login-other-page">
    <div class="contents">

      <div class="bread-box">
        <div class="inner">
          <ul class="bread-list-box">
            <li class="bread-list"><a href="/" class="bread-link">Eチケトップ</a></li>
            <li class="bread-list">各種会員IDをお持ちの方</li>
          </ul>
        </div>
      </div>

      <section class="bg-contents">
        <div class="inner">
          <h2 class="page-ttl">各種会員IDをお持ちの方</span></h2>
          <div class="sub-contents">
            <!-- <h3 class="common-title">各種会員IDをお持ちの方</h3> -->
            <form action="${_context.route_path('extauth.login',_query=request.GET)}" method="POST">
              <table class="login-tbl">
                <tr>
                  <td colspan="2">
                    <p class="img-id-rank"><img src="${view_context.static_url('images/member-id-rank.png')}" alt=""></p>
                  </td>
                </tr>
                <tr>
                  <th class="login-ttl">${h.auth_identifier_field_name(member_set)}</th>
                  <td class="login-cts"><input type="text" class="text" name="username" value="${username}" placeholder="Login ID" /></td>
                </tr>
                <tr>
                  <th class="login-ttl">${h.auth_secret_field_name(member_set)}</th>
                  <td class="login-cts">
                    <input type="password" name="password" value="${password}" placeholder="Password" />
                    % if message:
                    <p>${message}</p>
                    % endif
                    <input type="hidden" name="member_set" value="${selected_member_set.name}" />
                    <input type="hidden" name="_" value="${request.session.get_csrf_token()}" />
                  </td>
                </tr>
              </table>
              <div class="btn-box">
                <button type="submit" class="btn btn-primary">次に進む/Login</button>

                <a href="${_context.route_path('extauth.entry')}" class="btn btn-default">TEAM EAGLESメンバーの方<span class="pc">、</span><br><br class="sp">一般の方はこちらから</a>

              </div>
            </form>
          </div>
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
  </div>
    <!-- .contents -->

<!--SiteCatalyst-->
<%
    sc = {"pagename": "login"}
%>
<%include file="../common/sc_basic.html" args="sc=sc" />
<!--/SiteCatalyst-->
