<%inherit file='../../templates/layout_2col.mako'/>

<%namespace name="fco" file="../../templates/formcomponents.mako"/>

<div class="row">
    <h3>${master_env.title}追加</h3>
	<a href="${request.route_path(master_env.join("create"), action="input")}">新規作成</a>
</div>

<div class="row">
<h4>${master_env.title}一覧</h4>

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
			 x = master_env.mapper(request, x) if master_env.mapper else x
			 %>
            <tr>
              %for k in display_fields:
			    <td>${getattr(x,k, "-")}</td>
              %endfor
              <td>
              <form action="${request.route_path(master_env.join("update"),action="input",id=x.id)}" method="POST">
              <button type="submit" class="btn btn-small btn-primary"><i class="icon-cog icon-white"> </i> Update</button>
              </form>
              <td>
              <form action="${request.route_path(master_env.join("delete"),action="confirm",id=x.id)}" method="POST">
              <button type="submit" class="btn btn-small btn-danger"><i class="icon-trash icon-white"> </i> Delete</button>
              </form>
              </td>
            </tr>
        %endfor
    </tbody>
</table>
${xs.pager()}
</div>
