<%inherit file="base_for_error_page.mako" />
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
            <h3 class="common-title">指定されたURLは正しくありません</h3>
            <p>
                <a href="/">トップへ戻る</a>
            </p>
          </div>
        </div>
      </section>

    </div>
    <!-- .contents -->

<!--SiteCatalyst-->
<%
    sc = {"pagename": "error-notfound"}
%>
<%include file="../common/sc_basic.html" args="sc=sc" />
<!--/SiteCatalyst-->
