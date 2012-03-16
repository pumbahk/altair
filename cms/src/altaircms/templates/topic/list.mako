<%inherit file='../layout_2col.mako'/>

<div class="row-fluid">
  <div>
      <h4>トピック追加</h4>
      <%include file="parts/form.mako"/>
  </div>
</div>

<hr/>

<div class="row-fluid">
    <h4>トピック</h4>

    %if topics:
        <table class="table table-striped">
            <thead>
            <tr>
              <th>タイトル</th>
              <th>トピックの種別</th>
              <th>公開開始日</th>
              <th>公開終了日</th>
              <th>内容</th>
              <th>表示順序</th>
              <th>公開禁止</th>
              <th>イベント以外のページ</th>
              <th>イベント</th>
              <th>全体に公開</th>
            </tr>
            </thead>
        <tbody>
        %for topic in topics['topics']:
        <tr>
            <td><a href="${request.route_path("topic", id=topic['id'])}">${topic['title']}</a></td>
            <td>${topic["kind"]}</td>
            <td>${topic["publish_open_on"]}</td>
            <td>${topic["publish_close_on"]}</td>
            <td>${topic['text'] if len(topic['text']) <= 20 else topic['text'][:20]+"..."}</td>
            <td>${topic["orderno"]}</td>
            <td>${topic["is_vetoed"]}</td>
            <td>${topic["page"].title if topic["page"] else "-"}</td>
            <td>${topic["event"].title if topic["event"] else "-"}</td>
            <td>${topic["is_global"]}</td>
        </tr>
        %endfor
        </tbody>
        </table>
    %else:
		<div class="alert alert-info">
			トピックは登録されていません。
		</div>
    %endif
</div>
