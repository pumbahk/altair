<%inherit file="base.mako" />

<div id="content" class="subpage">
    <article>
        <h2>ログイン</h2>
        <section>
            <form method="post" accept-charset="utf-8" action="${_context.route_path('extauth.login',_query=request.GET)}">
                <input type="hidden" name="member_set" value="${selected_member_set.name}" />
                <input type="hidden" name="_" value="${request.session.get_csrf_token()}" />
                <dl class="form1 formall">
                    <dt>ログインID※半角英数</dt>
                    <dd><input type="text" name="username" id="username" placeholder="例:123456"/></dd>
                    <dt>パスワード※半角英数</dt>
                    <dd><input type="password" name="password" autocomplete="off" id="password" value="" placeholder="例:123456"/></dd>
                </dl>
                <p class="txtC">
                    <button class="btn" type="submit">ログイン</button>
                </p>
            </form>
        </section>
    </article>
</div>