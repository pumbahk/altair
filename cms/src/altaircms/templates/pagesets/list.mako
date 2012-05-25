<%inherit file='../layout_2col.mako'/>
<%
seq = h.paginate(request, pagesets, item_count=len(pagesets))
%>

${seq.pager()}
<table class="table">
  <tr>
	<th>Name</th>
	<th>URL</th>
  </tr>
  %for ps in seq.paginated():
  <tr>
	<td>
	  <a href="${request.route_url('pageset', pageset_id=ps.id)}">${ps.name}</a>
	</td>
	<td>${ps.url}</td>
  </tr>
  %endfor
</table>
${seq.pager()}
