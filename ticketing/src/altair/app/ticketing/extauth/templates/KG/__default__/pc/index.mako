<%inherit file="base.mako" />
<% member_set = _context.member_sets[0] %>
<div id="content" class="subpage">
<!-- subpage start -->
  <article>
    <h2>ログイン</h2>
    <section>
      <!-- pollux fanclub Box -->
      <div class="login-box">
<%doc>        <h3>会員の方はこちら</h3>
        <p class="txtC">
        % if oauth_service_providers:
          % for provider in oauth_service_providers:
            <a style="min-height: 40px;" href="${_context.route_path('extauth.fanclub.entry', _query=dict(service_provider_name=provider.name))}" class="btn">
            <%
            if len(provider.display_name) > 15:
              pct = 68
            else:
              pct = 100
            %>
              <span style="font-size:${pct}%">${provider.display_name}</span>
            </a>
          % endfor
        % else:
            <a href="${_context.route_path('extauth.fanclub.entry')}" class="btn">ログイン</a>
        % endif
        </p></%doc>
        <p class="txtL150">
            ①事前に会員登録が必要です。<br/>
            ②ご予約いただいたチケットの変更・キャンセルはお受けできません。<br/>
            ③チケットはいかなる場合も再発行いたしません。<br/>
            ④チケット取扱いのない公演もございます。<br/>
            ⑤チケット販売開始日はつながりにくくなる場合がございます。<br/>
            ⑥予約途中に接続が中断した場合、ご予約が完了しない場合がございます 。<br/>
            （誤って二重に予約されないようご注意ください）<br/><br/>

            ※お支払・お受取・手数料等の詳細は <a href='https://www.kyoto-gekijo.com/ticket/index.html' target='_blank'>こちら</a> をご覧ください。<br/>
        </p>
        <p class="txtC">
            <a style="min-height: 40px;" href="https://kyoto-gekijo.tstar.jp/fc/members/login" class="btn">
                <span>次へ</span>
             </a>
        </p>
      </div>
      <!-- pollux fanclub Box -->

      <!-- Guest Box-->
<%doc>      <div class="login-box">
        <h3>初めてご利用のお客様</h3>

        <form action="${_context.route_path('extauth.login',_query=request.GET)}" method="POST">
          <p class="txtC">
            <button type="submit" name="doGuestLoginAsGuest" class="btn">今すぐ登録する</button>
          </p>
          <input type="hidden" name="member_set" value=${member_set.name} />
          <input type="hidden" name="_" value="${request.session.get_csrf_token()}" />
        </form>
      </div></%doc>
      <!-- Guest Box-->

      <!-- Extauth Box
      <div class="login-box">
        <h3>各種IDをお持ちの方はこちら</h3>
        <p class="txtC">
          <a href="${_context.route_path('extauth.login', _query=dict(member_set=member_set.name))}" class="btn">ログイン</a>
        </p>
      </div>
       Extauth Box-->
    </section>
  </article>
<!-- subpage end -->
</div>
