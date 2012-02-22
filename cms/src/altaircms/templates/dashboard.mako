<%inherit file='layout.mako'/>

<div class="row">
    <div class="span2 pull-right">
        <div class="btn-group">
            <a class="btn dropdown-toggle" data-toggle="dropdown" href="#">
                サイト
                <span class="caret"></span>
            </a>
            <ul class="dropdown-menu">
                <li><a href="#">ticket.rakuten.co.jp</a></li>
            </ul>
        </div>
    </div>
    <div class="span6">
        <h4>最近のお知らせ</h4>

    </div>
</div>

<h1>dashboard</h1>
<ul>
    <!-- <li><a href="/client">edit client</a></li> -->
    <li><a href="${request.route_url("layout_list")}">レイアウト</a></li>
    <li><a href="${request.route_url("event_list")}">イベント</a></li>
    <li><a href="${request.route_url("asset_list")}">アセット</a></li>
    <li><a href="${request.route_url("widget_list")}">ウィジェット</a></li>
    <li><a href="${request.route_url("page_list")}">ページ</a></li>
</ul>
