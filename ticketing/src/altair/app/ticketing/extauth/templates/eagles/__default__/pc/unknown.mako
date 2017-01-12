<%inherit file="base_for_error_page.mako" />
<%
member_set = _context.member_sets[0]
guest_member_kinds = [member_kind for member_kind in member_set.member_kinds if member_kind.show_in_landing_page and member_kind.enable_guests]
%>

    <div class="contents">

      <div class="bread-box">
        <div class="inner">
          <ul class="bread-list-box">
            <li class="bread-list"><a href="/" class="bread-link">Eチケトップ</a></li>
            <li class="bread-list">エラー</li>
          </ul>
        </div>
      </div>

      <section class="bg-contents">
        <div class="inner">
          <h2 class="page-ttl">エラー</h2>
          <div class="sub-contents">
            <h3 class="common-title">ファンクラブ連携が確認できません（E011）</h3>
            <p>
                アクセス混雑などのため、現在ページが表示しにくい状態となっております。<br>
                お客様にはご迷惑をおかけしますが、今しばらくお待ち頂き、再度アクセスをお願いいたします。<br>
                <a href="/">トップへ戻る</a>
            </p>
          </div>
        </div>
      </section>

    </div>
    <!-- .contents -->

<!--SiteCatalyst-->
<%
    sc = {"pagename": "error-unknown"}
%>
<%include file="../common/sc_basic.html" args="sc=sc" />
<!--/SiteCatalyst-->
