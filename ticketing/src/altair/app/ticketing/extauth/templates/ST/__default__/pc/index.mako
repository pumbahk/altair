<%inherit file="base.mako" />
<%block name="css">
  <style>
    .notice {
      font-family: Arial, Verdana, serif;
      text-align: center;
    }
    .notice span {
      font-size: 13.3333px;
    }
    .notice .red-member {
      color: red;
    }
    .notice .blue-member {
      color: blue;
    }
    .notice .red-member,
    .notice .blue-member {
      font-size: 120%;
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
        <br>
        <br>
        <h3>無料会員の方はこちら</h3>
        <br>
        <p class="txtC">
          <a href="${_context.route_path('extauth.fanclub.entry')}" class="btn">ログイン</a>
        </p>
        <p class="txtC">
          <a href="//${request.host}/fc/members/select-membership">※会員登録はこちら</a>
        </p>
        <br/>
        <h3>会員パスワード再設定のお願い</h3>
        <br/>
        <div class="notice">
          <div><span>会員カテゴリ『classRED/classBLUE』の廃止に伴い、会員パスワードの再設定、または新規登録が必要となります。</span></div>
          <br/>
          <div class="blue-member">旧class BLUE会員の方</div>
          <div><span>会員ID(メールアドレス)は、ご登録頂いているIDで引き続きご利用可能です。</span></div>
          <div><span>下記のパスワード再設定ページより旧class BLUE会員で登録された氏名、メールアドレスをご入力の上、パスワードの再設定をお願いいたします。</span></div>
          <br/>
          <div><span><a href="https://sma-ticket.tstar.jp/fc/members/forgot-password">https://sma-ticket.tstar.jp/fc/members/forgot-password</a></span></div>
          <br/>
          <div class="red-member">旧class RED会員の方</div>
          <div><span>新規でのご登録が必要となります。</span></div>
          <div><span>下記の新規会員登録ページよりご登録をお願いいたします。</span></div>
          <br/>
          <div><span><a href="https://sma-ticket.tstar.jp/fc/members/select-membership">https://sma-ticket.tstar.jp/fc/members/select-membership</a></span></div>
          <br/>
          <div class="important">※パスワードの再設定、新規会員登録の際は事前に「@mail.tstar.jp」からのメールを受信できるようにドメイン指定受信許可設定をご確認ください。</div>
          <br/>
          <div>本件に関するお問い合わせ先</div>
          <div><span><a href="mailto:sma-ticket@tstar.jp">sma-ticket@tstar.jp</a></span></div>
        </div>
      </div>
      <!-- ファンクラブ Box-->
    </section>
  </article>
  <!-- subpage end -->
</div>
