<%inherit file='layout.mako'/>

<div class="row">
    <div class="span8">
        <h4>お知らせ</h4>
        <table class="table table-striped">
            <tbody>
            <tr>
                <td>199x/1/23</td>
                <td>世界は核の炎に包まれた</td>
            </tr>
            <tr>
                <td>199x/1/23</td>
                <td>世界は核の炎に包まれた</td>
            </tr>
            </tbody>
        </table>

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
