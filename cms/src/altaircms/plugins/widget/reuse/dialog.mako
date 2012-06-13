## reuse widget dialog
##  view function is views.ReuseWidgetView.dialog
##

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

<div class="title">
  <h1>再利用(todo rename)</h1>
</div>

<table class="table">
  <tbody>
    ${formfield("source_page_id")}
    ${formfield("width")}
    ${formfield("height")}
  </tbody>
</table>
<button type="button" id="reuse_submit">登録</button>
