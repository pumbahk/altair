<div class="box">
  <table class="table">
	<thead>
	  <tr>
		<th>タグの種類</th><th></th><th>タグの種類</th><th>作成日時</th><th>更新日時</th>
	  </tr>
	</thead>
	<tbody>
<%
tags = public_tags
tagsize = len(tags)
%>
	  <tr>
		<td rowspan="${tagsize}">公開タグ</td>
		%if tags:
		<td>
          <input type="checkbox" name="object_id" value="${tags[0].id}">
		</td>
		  <td>${tags[0].label}</td>
		  <td>${h.base.jdate(tags[0].created_at)}</td>
		  <td>${h.base.jdate(tags[0].updated_at)}</td>
		%endif
	  </tr>
	  %if tagsize >1:
	  %for tag in tags[1:]:
	  <tr>
		<td>
          <input type="checkbox" name="object_id" value="${tag.id}">
		</td>
		<td>${tag.label}</td>
		<td>${h.base.jdate(tag.created_at)}</td>
		<td>${h.base.jdate(tag.updated_at)}</td>
	  </tr>
	  %endfor
	  %endif
<%
tags = private_tags
tagsize = len(tags)
%>
	  <tr>
		<td rowspan="${tagsize}">非公開タグ</td>
		%if tags:
		  <td>
			<input type="checkbox" name="object_id" value="${tags[0].id}">
		  </td>
		  <td>${tags[0].label}</td>
		  <td>${h.base.jdate(tags[0].created_at)}</td>
		  <td>${h.base.jdate(tags[0].updated_at)}</td>
		%endif
	  </tr>
	  %if tagsize >1:
	  %for tag in tags[1:]:
	  <tr>
		<td>
          <input type="checkbox" name="object_id" value="${tag.id}">
		</td>
		<td>${tag.label}</td>
		<td>${h.base.jdate(tag.created_at)}</td>
		<td>${h.base.jdate(tag.updated_at)}</td>
	  </tr>
	  %endfor
	  %endif
	</tbody>
  </table>
  <div class="btn-group">
    <a href="${request.route_path("performance_update",action="input",id="__id__")}" class="btn action">
      <i class="icon-pencil"></i> タグの追加
    </a>
    <button class="btn dropdown-toggle" data-toggle="dropdown">
        <span class="caret"></span>
    </button>
    <ul class="dropdown-menu">
    </ul>
  </div>
</div>