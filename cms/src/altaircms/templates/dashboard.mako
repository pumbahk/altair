<%inherit file='layout.mako'/>
<h1>dashboard</h1>
<ul>
    <!-- <li><a href="/client">edit client</a></li> -->
    <li><a href="${request.route_url("layout_list")}">レイアウト</a></li>
    <li><a href="${request.route_url("event_list")}">イベント</a></li>
    <li><a href="${request.route_url("asset_list")}">アセット</a></li>
    <li><a href="${request.route_url("widget_list")}">ウィジェット</a></li>
    <li><a href="${request.route_url("page_list")}">ページ</a></li>
</ul>
