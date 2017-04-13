<%inherit file="base.mako" />
<% member_set = _context.member_sets[0] %>
<div id="content" class="subpage">
<!-- subpage start -->
    <article>
        <h2>ご選択ください</h2>
        <section>
            <!-- ファンクラブ Box-->
            <div class="login-box">
                <h3>会員の方はこちら</h3>
                <p class="txtC">
                    <a href="${_context.route_path('extauth.fanclub.entry')}" class="btn">ログイン</a>
                </p>
                <p class="txtC">
                    <a href="//${request.host}/fc/members/select-membership">※無料会員登録はこちら</a>
                </p>
            </div>
            <!-- ファンクラブ Box-->

            <!-- Gest Box-->
            <div class="login-box">
                <h3>ゲスト申込の方はこちら(会員登録なし)</h3>

                <form action="${_context.route_path('extauth.login',_query=request.GET)}" method="POST">
                    <p class="txtC">
                        <button type="submit" name="doGuestLoginAsGuest" class="btn">申込</button>
                    </p>
                    <input type="hidden" name="member_set" value=${member_set.name}>
                    <input type="hidden" name="_" value="${request.session.get_csrf_token()}" />
                </form>
            </div>
            <!-- Gest Box-->

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
