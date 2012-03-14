<%inherit file='../layout_2col.mako'/>

<div class="row" style="margin-bottom: 9px">
  <h2 class="span6">更新 ページのタイトル - ${page.title} (ID: ${page.id})</h2>
</div>

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
  <div class="span5">
	<form action="${h.page.to_update_confirm(request,page)}" method="POST">
      <table class="table">
        <tbody>
          ${formfield("title")}
          ${formfield("url")}
          ${formfield("description")}
          ${formfield("keywords")}
          ${formfield("tags")}
          ${formfield("layout")}
        </tbody>
      </table>
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> Update</button>
    </form>
  </div>
</div>
