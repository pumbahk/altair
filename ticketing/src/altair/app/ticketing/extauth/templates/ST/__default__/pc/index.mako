<%inherit file="base.mako" />
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
            </div>
            <!-- ファンクラブ Box-->
        </section>
    </article>
<!-- subpage end -->
</div>
