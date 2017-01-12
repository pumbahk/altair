<div class="ts-wrapper">

<!-- ******************** header [start] ******************** -->
<header class="ts-header">
% if hasattr(_context, 'subtype') and request.authenticated_userid:
ログイン中 (<a href="${request.route_path('extauth.logout', subtype=_context.subtype)}">ログアウトする</a>)
% endif
<div class="ts-header-inner">

<!-- ===== ts-header-wrap [start] ===== -->
<div class="ts-header-wrap">

<div class="ts-header-logobox clearfix">
<img src="${view_context.static_url('images/pc_logo.png')}" alt="logo" width="100%" />
</div>

</div><!-- ===== ts-header-wrap [end] ===== -->

</div></header><!-- ******************** header [end] ******************** -->

<!-- ******************** contents [start] ******************** -->
<div class="ts-contents">
<div class="ts-contents-inner">