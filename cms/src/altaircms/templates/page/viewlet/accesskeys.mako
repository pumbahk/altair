<div class="box">
  <table class="table">
	<thead>
	  <tr>
      <th></th>
		%for k in labels:
		  <th>${k}</th>
		%endfor
	  </tr>
	</thead>
	<tbody>
	  %for x in accesskeys:
        <tr>
		  <td>
			<input type="radio" name="object_id" value="${x.id}">
		  </td>
          <td>
            ${request.route_url("preview_page", page_id=page.id, _query=dict(access_key=x.hashkey))}
          </td>
		  %for k in display_fields:
			  <td>${getattr(x,k)}</td>
		  %endfor
		  </td>
		</tr>
	  %endfor
	</tbody>
  </table>
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
  </div>
</div>
