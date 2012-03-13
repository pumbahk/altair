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
                <th>トピック名</th>
                <th>トピックの種類</th>
                <th>公開日</th>
                <th>内容</th>
            </tr>
            </thead>
        <tbody>
        %for topic in topics['topics']:
        <tr>
            <td><a href="${request.route_url("topic", id=topic['id'])}">${topic['title']}</a></td>
            <td>${topic['kind']}</td>
            <td>${topic['publish_at']}</td>
            <td>${topic['text']}</td>
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
