<%inherit file="base.mako" />
    <div class="login-member-page">
      <div class="contents">

        <div class="bread-box">
          <div class="inner">
            <ul class="bread-list-box">
              <li class="bread-list"><a href="/" class="bread-link">Eチケトップ</a></li>
              <li class="bread-list">TEAM EAGLESメンバー選択</li>
            </ul>
          </div>
        </div>

        <section class="bg-contents">
          <div class="inner">
            <h2 class="page-ttl">TEAM EAGLESメンバー選択</h2>

            <table class="login-tbl">
%for membership in memberships:
<%
    if membership['kind']['name'] == u'5-STAR': class_for_club='login-five-star'
    elif membership['kind']['name'] == u'4-STAR': class_for_club='login-four-star'
    elif membership['kind']['name'] == u'3-STAR': class_for_club='login-three-star'
    elif membership['kind']['name'] == u'2-STAR': class_for_club='login-two-star'
    elif membership['kind']['name'] == u'KIDS': class_for_club='login-kids-star'
    elif membership['kind']['name'] == u'アカデミー': class_for_club='login-academy'
    elif membership['kind']['name'] == u'TEAM EAGLES ROOKIE': class_for_club='login-teameaglesrookie'
    elif membership['kind']['name'] == u'KIDS(KIDS2)': class_for_club='login-kidstwo'
    else: class_for_club='login-basic-club'
%>
              <tr>
                <td class="login-box ${class_for_club}">
                  <h3 class="sub-ttl">${membership['kind']['name']}</h3>
                  <p class="member-id">会員ID：${membership['displayed_membership_id']}</p>
                  <div class="btn-box">
                    <a href="${_context.route_path('extauth.authorize', _query=dict(_=request.session.get_csrf_token(), member_kind_id=membership['kind']['id'], membership_id=membership['membership_id']))}" class="btn btn-team">
                      <span>選択する</span>
                    </a>
                  </div>
                </td>
              </tr>
%endfor
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
    <!-- .login-member-page -->

<!--SiteCatalyst-->
<%
    sc = {"pagename": "select_account"}
%>
<%include file="../common/sc_basic.html" args="sc=sc" />
<!--/SiteCatalyst-->
