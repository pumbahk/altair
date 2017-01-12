<%inherit file="base.mako" />
    <div class="login-member-page">
      <div class="contents">

        <div class="bread-box">
          <div class="inner">
            <ul class="bread-list-box">
              <li class="bread-list"><a href="/" class="bread-link">Eチケトップ</a></li>
              <li class="bread-list">ファンクラブ会員選択</li>
            </ul>
          </div>
        </div>

        <section class="bg-contents">
          <div class="inner">
            <h2 class="page-ttl">ファンクラブ会員選択</h2>

            <table class="login-tbl">
%for membership in memberships:
<%
    if membership['kind']['name'] == u'ブースタークラブ': class_for_club='login-booster-club'
    elif membership['kind']['name'] == u'スーパーゴールドクラブ': class_for_club='login-super-gold-club'
    elif membership['kind']['name'] == u'ゴールドクラブ': class_for_club='login-gold-club'
    elif membership['kind']['name'] == u'レギュラークラブ': class_for_club='login-regular-club'
    elif membership['kind']['name'] == u'レディースクラブ': class_for_club='login-ladies-club'
    elif membership['kind']['name'] == u'学生クラブ': class_for_club='login-school-club'
    elif membership['kind']['name'] == u'キッズクラブ': class_for_club='login-kids-club'
    elif membership['kind']['name'] == u'ベーシッククラブ': class_for_club='login-basic-club'
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
                <p class="info-txt">楽天野球団チケットセンター<br>TEL:050-5817-8192（10:00〜18:00）</p>
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
