<%inherit file='../layout_2col.mako'/>
<table class="table">
<tr>
<th>Name</th>
<th>URL</th>
</tr>
%for ps in pagesets:
<tr>
<td>
<a href="${request.route_url('pageset', pageset_id=ps.id)}">${ps.name}</a>
</td>
<td>${ps.url}</td>
</tr>
%endfor
</table>