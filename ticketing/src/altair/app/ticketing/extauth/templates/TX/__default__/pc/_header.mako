<!-- header start -->
<header>
    <div class="head">
        <h1>
            <a href="https://www.tokairadio.co.jp/event/">
            <img src="${view_context.static_url('images/logo.png')}" alt="logo">
            </a>
        </h1>
    </div>
    % if hasattr(_context, 'subtype') and request.authenticated_userid:
        ログイン中 (<a href="${request.route_path('extauth.logout', subtype=_context.subtype)}">ログアウトする</a>)
    % endif
</header>
<!-- header end -->