<%inherit file="/_base.mako" />
% if not request.authenticated_userid:
    <%block name="title">トップページ</%block>
    <a href="${request.route_path('login')}">ログインする</a>
% endif
<p>
hogehoge
${h.test_helper()}
<a href="${request.route_path("example.page_needs_authentication")}">権限の必要なページ</a>
</p>
