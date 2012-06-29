<div class="box">
  <table class="table">
	<thead>
	  <tr>
		<td></td>
		%for k in labels:
		  <th>${k}</th>
		%endfor
	  </tr>
	</thead>
	<tbody>
	  %for word in hotwords:
<% mapped = mapper(word) %>
        <tr>
		  <td>
			<input type="checkbox" name="object_id" value="${mapped.id}">
		  </td>
		  %for k in display_fields:
			  <td>${getattr(mapped,k)}</td>
		  %endfor
		  </td>
		</tr>
	  %endfor
	</tbody>
  </table>
    <ul class="dropdown-menu">
      <li>
        <a href="${request.route_path("hotword_update",action="detail",id="__id__")}" class="action">
          <i class="icon-pencil"></i> 詳細画面
        </a>
      </li>
      <li>
        <a href="${request.route_path("hotword_update",action="input",id="__id__")}" class="action">
          <i class="icon-minus"></i> 編集
        </a>
      </li>
      <li>
        <a href="${request.route_path("hotword_create",action="input")}">
          <i class="icon-minus"></i> 新規作成
        </a>
      </li>
      <li>
        <a href="${request.route_path("hotword_delete",action="confirm",id="__id__")}" class="action">
          <i class="icon-minus"></i> 削除
        </a>
      </li>
    </ul>
  </div>
</div>
