<%inherit file='../../templates/layout_2col.mako'/>

<%namespace name="fco" file="../../templates/formcomponents.mako"/>

<div class="row">
    <h3>${master_env.title}追加・一覧</h3>
    <form action="${request.route_path(master_env._join("create"))}" method="POST">
       ${fco.form_as_table_strict(form, display_fields)}
        <button class="btn" type="submit">保存</button>
    </form>
</div>

<div class="row">
<h4>${master_env.title}一覧</h4>
<table class="table table-striped">
  <thead>
	<tr>
      %for k in display_fields:
      <th>${getattr(form,k).label}</th>
      %endfor
	</tr>
  </thead>
    <tbody>
        %for x in xs:
		    <%
			 x = master_env.mapper(request, x) if master_env.mapper else x
			 %>
            <tr>
              %for k in display_fields:
			    <td>${getattr(x,k, "-")}</td>
              %endfor
              <td>
              <form action="${request.route_path(master_env._join("delete"),id=x.id)}" method="POST">
              <button type="submit" class="btn btn-small btn-danger"><i class="icon-trash icon-white"> </i> Delete</button>
              </form>
              </td>
            </tr>
        %endfor
    </tbody>
</table>
</div>
