<ul class="nav nav-list">
    <li class="nav-header">イベント管理</li>
    <!-- <li><a href="/client">edit client</a></li> -->
    <li><a href="${request.route_url("event_list")}">イベント</a></li>
    <li><a href="#">パフォーマンス</a></li>
    <li><a href="#">トピック</a></li>

    <li class="nav-header">ページ管理</li>
    <li><a href="${request.route_url("layout_list")}">レイアウト</a></li>
    <li><a href="${request.route_url("page")}">ページ</a></li>

    <li class="nav-header">アセット管理</li>
    <li><a href="${request.route_url("asset_list")}">アセット</a></li>

    <li class="nav-header">その他</li>
    <li><a href="#">メールマガジン</a></li>
    <li><a href="${request.route_url("operator_list")}">オペレータ</a></li>
    <li>タグ</li>
    <li><a href="${request.route_url("apikey_list")}">APIKEY</a></li>
    <li>ロール</li>
</ul>
