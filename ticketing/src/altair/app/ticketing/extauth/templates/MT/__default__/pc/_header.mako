<!-- header start -->
<style type="text/css">
@media screen and (max-width: 410px) {
    header .head h1 img {
        width: 100%;
    }
}
</style>
<header>
    <div class="head">
        <h1>
            <img src="${view_context.static_url('images/logo.png')}" alt="logo">
        </h1>
    </div>
    % if hasattr(_context, 'subtype') and request.authenticated_userid:
        ログイン中 (<a href="${request.route_path('extauth.logout', subtype=_context.subtype)}">ログアウトする</a>)
    % endif
</header>
<!-- header end -->
