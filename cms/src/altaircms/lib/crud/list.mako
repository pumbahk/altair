<%inherit file='../../templates/layout_2col.mako'/>

<%def name="formfield(form,k)">
	<tr><th>${getattr(form,k).label}</th><td>${getattr(form,k)}
	%if k in form.errors:
	  <br/>
	  %for error in form.errors[k]:
		<span class="btn btn-danger">${error}</span>
	  %endfor
	%endif
	</td></tr>
</%def>

<div class="row">
    <h3>${master_env.title}追加・一覧</h3>
    <form action="${request.route_path(master_env._join("create"))}" method="POST">
        <table class="table">
            <tbody>
              %for k in display_fields:
    			  ${formfield(form, k)}
              %endfor
            </tbody>
        </table>
        <button class="btn" type="submit">保存</button>
    </form>
</div>

<div class="row">
<h4>${master_env.title}一覧</h4>
<table class="table table-striped">
    <tbody>
        %for x in xs:
            <tr>
              %for k in display_fields:
    			  <td>${k}</td><td>${getattr(x,k) or "-"}</td>
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
