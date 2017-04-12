<!-- header start -->
<header>
    <div class="head">
        <img src="${view_context.static_url('images/logo.png')}" alt="logo">
    </div>
    % if hasattr(_context, 'subtype') and request.authenticated_userid:
        ログイン中 (<a href="${request.route_path('extauth.logout', subtype=_context.subtype)}">ログアウトする</a>)
    % endif
</header>
<!-- header end -->
