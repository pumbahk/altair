<div class="box">
  <table class="table">
	<thead>
	  <tr>
		<th>タグの種類</th>
		##<th></th>
		<th>タグの種類</th>
		<th>作成日時</th>
	  </tr>
	</thead>
	<tbody>
<%
tags = public_tags
tagsize = len(tags)
%>
	  <tr class="public">
		<td rowspan="${tagsize}">公開タグ</td>
		%if tags:
##		<td>
##          <input type="checkbox" name="object_id" value="${tags[0].id}">
##		</td>
		  <td><a class="tag" href="${h.tag.to_search_query(request, "page", tags[0])}">${tags[0].label}</a></td>
		  <td>${h.base.jdate(tags[0].created_at)}</td>
		%endif
	  </tr>
	  %if tagsize >1:
	  %for tag in tags[1:]:
	  <tr class="public">
##		<td>
##          <input type="checkbox" name="object_id" value="${tag.id}">
##		</td>
		<td><a class="tag" href="${h.tag.to_search_query(request, "page", tag)}">${tag.label}</a></td>
		<td>${h.base.jdate(tag.created_at)}</td>
	  </tr>
	  %endfor
	  %endif
<%
tags = private_tags
tagsize = len(tags)
%>
	  <tr class="private">
		<td rowspan="${tagsize}">非公開タグ</td>
		%if tags:
##		  <td>
##			<input type="checkbox" name="object_id" value="${tags[0].id}">
##		  </td>
		  <td><a class="tag" href="${h.tag.to_search_query(request, "page", tag)}">${tags[0].label}</a></td>
		  <td>${h.base.jdate(tags[0].created_at)}</td>
		%endif
	  </tr>
	  %if tagsize >1:
	  %for tag in tags[1:]:
	  <tr class="private">
##		<td>
##          <input type="checkbox" name="object_id" value="${tag.id}">
##		</td>
		<td><a class="tag" href="${h.tag.to_search_query(request, "page", tag)}">${tag.label}</a></td>
		<td>${h.base.jdate(tag.created_at)}</td>
	  </tr>
	  %endfor
	  %endif
	</tbody>
  </table>
<%doc>
  <div class="btn-group">
    <a href="${request.route_path("performance_update",action="input",id="__id__")}" class="btn action">
      <i class="icon-pencil"></i> タグの追加
    </a>
    <button class="btn dropdown-toggle" data-toggle="dropdown">
        <span class="caret"></span>
    </button>
    <ul class="dropdown-menu">
	  <li>
		<a id="page_tag_delete_tag" href="${request.route_path("plugins_jsapi_page_tag_delete",page_id=page.id)}">
		  <i class="icon-minus"></i>選択したタグの削除
	  </li>
    </ul>
  </div>
  <script type="text/javascript">
	$(function(){
	  $("#page_tag_delete_tag").click(function(e){
	    e.preventDefault();
	    var root = $(this).parents(".box");
	    tags = root.find(".public input[name='object_id']:checked");
        private_tags = root.find(".private input[name='object_id']:checked");

	    var publics = [];
	    for(var i=0,j=tags.length; i<j; i++){
	      publics[i] = $(tags[i]).val();
	    }

	    var privates = [];
	    for(var i=0,j=private_tags.length; i<j; i++){
	      privates[i] = $(private_tags[i]).val();
	    }

        $.post($(this).attr("href"),{"tags": publics, "private_tags": privates}).done(function(){ location.reload();});
	  });
	})
  </script>
</%doc>
</div>
