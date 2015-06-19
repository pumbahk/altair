<%inherit file="/_base.mako" />
<%block name="title">トップページ</%block>
<p>
hogehoge
${h.test_helper()}
<a href="${request.route_path("example.page_needs_authentication")}">権限の必要なページ</a>
</p>
