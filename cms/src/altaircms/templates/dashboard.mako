<%inherit file='layout_2col.mako'/>
<div class="row">
    <div class="span8">
        <h4>お知らせ</h4>
        <table class="table table-striped">
            <tbody>
            <tr>
                <td>199x/1/23</td>
                <td>testtest</td>
            </tr>
            <tr>
                <td>199x/1/23</td>
                <td>testtest</td>
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
          %for event in events:
        <tr>
          <td>${event.event_open}</td><td><a href="${request.route_path("event", id=event.id)}">${event.title}</a></td>
        </tr>
          %endfor
      </table>
    </div>
</div>

<div class="well">
<p class="lead">はじめ</p>
<ul style="font-size:150%;">
  <li><a href="${request.route_path("event_list")}">イベント関連のページを編集する</a></li>
  <li><a href="${request.route_path("page_list",kind="other")}">トップページのカテゴリトップページなどを編集する</a></li>
  <li><a>静的なページの編集をする</a></li>
</ul>
</div>
