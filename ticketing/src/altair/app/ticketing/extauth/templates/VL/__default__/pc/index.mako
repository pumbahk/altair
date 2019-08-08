<%inherit file="base.mako" />
<%block name="css">
  <style>
    .notice {
      max-width: 95%;
      margin: 0 auto;
      font-size: 13.3333px;
    }
  </style>
</%block>
<% member_set = _context.member_sets[0] %>
<div id="content" class="subpage">
  <!-- subpage start -->
  <article>
    <h2>　　</h2>
    <section>
      <!-- ファンクラブ Box-->
      <div class="login-box">
        <h3>会員の方はこちら</h3>
        <p class="txtC">
          <a href="${_context.route_path('extauth.fanclub.entry')}" class="btn">ログイン</a>
        </p>
        <p class="txtC">
          <a href="//${request.host}/fc/members/select-membership">※会員登録はこちら</a>
        </p>
      </div>
      <!-- ファンクラブ Box-->

      <br/>
      <h3>会員パスワード再設定のお願い</h3>
      <br/>
      <div class="notice">
        <div>チケット販売システムの切換えリニューアルに伴い、会員パスワードの再設定が必要となります。</div>
        <br/>
        <div>会員ID(メールアドレス)は、ご登録頂いているIDで引き続きご利用可能です。</div>
        <br/>
        <div>下記のパスワード再設定ページより旧会員で登録された氏名、メールアドレスをご入力の上、パスワードの再設定をお願いいたします。</div>
        <br/>
        <div><a href="https://vorlesen.tstar.jp/fc/members/forgot-password">パスワード再設定はこちら</a></div>
        <br/>
        <div>※パスワードの再設定の際は事前に「@mail.tstar.jp」からのメールを受信できるようにドメイン指定受信許可設定をご確認ください。</div>
      </div>
    </section>
  </article>
  <!-- subpage end -->
</div>
