<%inherit file='../layout_2col.mako'/>

<%def name="formfield(k)">
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
    <h3>ページ追加・一覧</h3>
    <%include file="../parts/formerror.mako"/>
    <form action="#" method="POST">
        <table class="table">
            <tbody>
			  ${formfield(form, )}
            </tbody>
        </table>
        <button class="btn" type="submit">保存</button>
    </form>
</div>

<div class="row">
<h4>ページ一覧</h4>
<table class="table table-striped">
    <tbody>
        %for page in pages:
            <tr>
                <td>${page.created_at}</td>
                <td>${page.url}</td>
                <td><a href="${request.route_path("page_edit_", page_id=page.id)}">${page.title}</a></td>
                <td>
                    <a href="${h.front.to_preview_page(request, page)}" class="btn btn-small"><i class="icon-eye-open"> </i> Preview</a>
                </td>
            </tr>
        %endfor
    </tbody>
</table>
</div>
