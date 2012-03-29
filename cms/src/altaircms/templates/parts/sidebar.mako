<ul class="nav nav-list">
    <li class="nav-header">イベント管理</li>
    <!-- <li><a href="/client">edit client</a></li> -->
    <li><a href="${request.route_path("event_list")}">イベント</a></li>
    <li><a href="#">パフォーマンス</a></li>
    <li><a href="${request.route_path("topic_list")}">トピック</a></li>
    <li><a href="${request.route_path("topcontent_list")}">トップコンテンツ</a></li>

    <li class="nav-header">ページ管理</li>
    <li><a href="${request.route_path("layout_list")}">レイアウト</a></li>
    <li><a href="${request.route_path("page")}">ページ</a></li>

    <li class="nav-header">アセット管理</li>
    <li><a href="${request.route_path("asset_list")}">アセット</a></li>

    <li class="nav-header">その他</li>
    <li><a href="#">メールマガジン</a></li>
    <li><a href="${request.route_path("operator_list")}">オペレータ</a></li>
    <li><a href="${request.route_path("apikey_list")}">APIKEY</a></li>
    <li><a href="${request.route_path("role_list")}">ロール</a></li>
    <li>タグ</li>
</ul>
