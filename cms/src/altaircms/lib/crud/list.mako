<%inherit file='../../templates/layout_2col.mako'/>

<%namespace name="fco" file="../../templates/formcomponents.mako"/>

<div class="row">
    <h3>${master_env.title}追加</h3>
	<a href="${request.route_path(context._join("create"), action="input")">新規作成</a>
</div>

<div class="row">
<h4>${context.title}一覧</h4>

${xs.pager()}
<table class="table table-striped">
  <thead>
	<tr>
      %for k in display_fields:
      <th>${getattr(form,k).label}</th>
      %endfor
	</tr>
  </thead>
    <tbody>
        %for x in xs.paginated():
		    <%
			 x = context.mapper(request, x) if context.mapper else x
			 %>
            <tr>
              %for k in display_fields:
			    <td>${getattr(x,k, "-")}</td>
              %endfor
              <td>
              <form action="${request.route_path(context.join("delete"),action="confirm",id=x.id)}" method="POST">
              <button type="submit" class="btn btn-small btn-danger"><i class="icon-trash icon-white"> </i> Delete</button>
              </form>
              </td>
            </tr>
        %endfor
    </tbody>
</table>
${xs.pager()}
</div>
