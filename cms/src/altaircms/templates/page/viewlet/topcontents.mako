<div class="box">
  <p><a href="#">${pageset.name}ページ</a>に直接結びついているものを表示</p>
  <table class="table">
	<thead>
	  <tr>
		<th></th>
		<th>タイトル</th>
        <th>画像</th>
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
     %for topcontent in topcontents:
  <tr>
	<td><input type="radio" name="object_id" value="${topcontent.id}"></td>
	<td>${topcontent.title}</td>
	<td><img src="${h.asset.to_show_page(request,topcontent.image_asset)}" width=50px height=50px/></td>
	<td>${topcontent.kind}</td>
	<td>${topcontent.subkind}</td>
	<td>${topcontent.publish_open_on}</td>
	<td>${topcontent.publish_close_on}</td>
	<td>${topcontent.orderno}</td>
    <td>${topcontent.is_vetoed}</td>
	<td><a href="${h.link.get_link_from_topcontent(request,topcontent)}">リンク先</a></td>
  </tr>
     %endfor
  </tbody>
  </table>

  <div class="btn-group">
    <a target="_blank" href="${request.route_path("topcontent_update",action="input", id="__id__")}" class="action btn">
      <i class="icon-minus"></i> 編集
    </a>
    <button class="btn dropdown-toggle" data-toggle="dropdown">
        <span class="caret"></span>
    </button>
    <ul class="dropdown-menu">
      <li>
        <a target="_blank" href="${request.route_path("topcontent_update",action="input", id="__id__")}" class="action">
          <i class="icon-minus"></i> 編集
        </a>
      </li>
      <li>
        <a target="_blank" href="${request.route_path("topcontent_create", action="copied_input",_query=dict(id="__id__"))}" class="action">
          <i class="icon-minus"></i> コピーして新規作成
        </a>
      </li>
      <li>
        <a target="_blank" href="${request.route_path("topcontent_create", action="input", _query=dict(bound_page=pageset.id))}">
          <i class="icon-minus"></i> 新規作成
        </a>
      </li>
      <li>
        <a target="_blank" href="${request.route_path("topcontent_delete", action="confirm", id="__id__")}" class="action">
          <i class="icon-minus"></i> 削除
        </a>
      </li>
    </ul>
  </div>
</div>
