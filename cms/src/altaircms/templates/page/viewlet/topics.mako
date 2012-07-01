<div class="box">
  <p><a href="#">${pageset.name}ページ</a>に直接結びついているものを表示</p>
  <table class="table">
	<thead>
	  <tr>
		<th></th>
		<th>タイトル</th>
		<th>トピックの種別</th>
		<th>サブ分類</th>
		<th>公開開始</th>
		<th>公開終了</th>
		<th>表示順序</th>
		<th>公開禁止</th>
        <th>リンク先</th>
	  </tr>
    </thead>
    <tbody>
     %for topic in topics:
  <tr>
	<td><input type="radio" name="object_id" value="${topic.id}"></td>
	<td>${topic.title}</td>
	<td>${topic.kind}</td>
	<td>${topic.subkind}</td>
	<td>${topic.publish_open_on}</td>
	<td>${topic.publish_close_on}</td>
	<td>${topic.orderno}</td>
    <td>${topic.is_vetoed}</td>
	<td><a href="${h.link.get_link_from_topic(request,topic)}">リンク先</a></td>
  </tr>
     %endfor
  </tbody>
  </table>

  <div class="btn-group">
    <a target="_blank" href="${request.route_path("topic_update",action="input", id="__id__")}" class="action btn">
      <i class="icon-minus"></i> 編集
    </a>
    <button class="btn dropdown-toggle" data-toggle="dropdown">
        <span class="caret"></span>
    </button>
    <ul class="dropdown-menu">
      <li>
        <a target="_blank" href="${request.route_path("topic_update",action="input", id="__id__")}" class="action">
          <i class="icon-minus"></i> 編集
        </a>
      </li>
      <li>
        <a target="_blank" href="${request.route_path("topic_create", action="input", _query=dict(bound_page=pageset.id))}">
          <i class="icon-minus"></i> 新規作成
        </a>
      </li>
      <li>
        <a target="_blank" href="${request.route_path("topic_delete", action="confirm", id="__id__")}" class="action">
          <i class="icon-minus"></i> 削除
        </a>
      </li>
    </ul>
  </div>
</div>
