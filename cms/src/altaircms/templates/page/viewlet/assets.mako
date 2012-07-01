<div class="box">
  <p>${taglabel}のタグがついているものを表示</p>
  <table class="table">
	<thead>
	  <tr>
		<th></th>
		<th></th>
		<th>タイトル</th>
		<th>登録日</th>
		<th>サイズ</th>
        <th>幅</th>
        <th>高さ</th>
	  </tr>
    </thead>
    <tbody>
     %for asset in assets:
  <tr>
	<td><input type="radio" name="object_id" value="${asset.id}"></td>
	<td><a href="${request.route_path("asset_image_detail",asset_id=asset.id)}"><img src="${h.asset.to_show_page(request,asset)}" width=50px height=50px/></a></td>
	<td>${asset.title}</td>
	<td>${asset.created_at}</td>
	<td>${asset.size}</td>
	<td>${asset.width}</td>
	<td>${asset.height}</td>
  </tr>
     %endfor
  </tbody>
  </table>

  <div class="btn-group">
	<a target="_blank" href="${request.route_path("asset_image_detail",asset_id="__id__")}" class="action btn">
      <i class="icon-pencil"></i> 詳細
    </a>
    <button class="btn dropdown-toggle" data-toggle="dropdown">
        <span class="caret"></span>
    </button>
    <ul class="dropdown-menu">
      <li>
        <a target="_blank" href="${request.route_path("asset_image_detail",asset_id="__id__")}" class="action">
          <i class="icon-pencil"></i> 詳細
        </a>
      </li>
      <li>
        <a target="_blank" href="${request.route_path("asset_image_input",asset_id="__id__")}" class="action">
          <i class="icon-minus"></i> 編集
        </a>
      </li>
      <li>
        <a target="_blank" href="${request.route_path("asset_add", kind="image",_query=dict(private_tags=taglabel))}">
          <i class="icon-minus"></i> 新規作成
        </a>
      </li>
      <li>
        <a target="_blank" href="${request.route_path("asset_image_delete", asset_id="__id__")}" class="action">
          <i class="icon-minus"></i> 削除
        </a>
      </li>
    </ul>
  </div>
</div>
