<div class="box">
  <table class="table">
	<thead>
	  <tr>
      <th></th>
	  <th>名前</th>
      <th>ハッシュ値</th>
	  <th>有効期限</th>
	  <th>作成日時</th>
	  </tr>
	</thead>
	<tbody>
	  %for x in accesskeys:
        <tr>
		  <td>
			<input type="radio" name="object_id" value="${x.id}">
		  </td>
		  <td>${x.name}</td>
          <td>
			${x.hashkey}　<a href="${request.route_url("preview_page", page_id=page.id, _query=dict(access_key=x.hashkey))}">クライアント確認用URL</a>
          </td>
		  <td>${ x.expiredate or u"期限指定なし" }</td>
		  <td>${ x.created_at }</td>
		</tr>
	  %endfor
	</tbody>
  </table>
  <div id="accesskey_btns" class="btn-group">
    <a href="${request.route_path("plugins_jsapi_accesskey",action="create", page_id=page.id)}" class="btn indivisual-action">
      <i class="icon-pencil"></i> アクセスキーの追加
    </a>
    <button class="btn dropdown-toggle" data-toggle="dropdown">
        <span class="caret"></span>
    </button>
    <ul class="dropdown-menu">
      <li>
        <a href="${request.route_path("hotword_update",action="detail",id="__id__")}" class="action">
          <i class="icon-pencil"></i> アクセスURLをクライアントに通知
        </a>
      </li>
      <li>
        <a href="${request.route_path("hotword_delete",action="confirm",id="__id__")}" class="action">
          <i class="icon-minus"></i> 削除
        </a>
      </li>
    </ul>
    <script type="text/javascript">
	  $("#accesskey_btns a.indivisual-action").click(function(e){
	    e.preventDefault();
	    var url = $(this).attr("href");
	    $.post(url).done(function(){ location.reload(); });
	  });
    </script>
  </div>
</div>
