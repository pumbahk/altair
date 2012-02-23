<%inherit file='layout.mako'/>

<div class="span2">
<ul class="nav nav-list">
    <li class="nav-header">イベント管理</li>
    <!-- <li><a href="/client">edit client</a></li> -->
    <li><a href="${request.route_url("event_list")}">イベント</a></li>
    <li><a href="#">パフォーマンス</a></li>
    <li><a href="#">トピック</a></li>

    <li class="nav-header">ページ管理</li>
    <li><a href="${request.route_url("layout_list")}">レイアウト</a></li>
    <li><a href="${request.route_url("page_list")}">ページ</a></li>
    <li><a href="${request.route_url("widget_list")}">ウィジェット</a></li>

    <li class="nav-header">アセット管理</li>
    <li><a href="${request.route_url("asset_list")}">アセット</a></li>

    <li class="nav-header">その他</li>
    <li><a href="#">メールマガジン</a></li>
</ul>
</div>

<div class="row">
    <div class="span6">
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
    <div class="span4">
      <h4>イベント</h4>
      <div class="btn-toolbar">
        <div class="btn-group">
          <a class="btn btn-small" href="#">もうすぐ公開</a>
          <a class="btn btn-small" href="#">条件付き</a>
        </div>
      </div>
      <table class="table table-striped">
        <tr>
          <td>2011/1/1</td><td>blueman live</td>
        </tr>
      </table>
    </div>
</div>

