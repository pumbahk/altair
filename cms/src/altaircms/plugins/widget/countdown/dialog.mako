## countdown widget dialog
##  view function is views.CountdownWidgetView.dialog
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
  <h1>カウントダウン(info)</h1>
</div>

<table class="table">
  <tbody>
    ${formfield("kind")}
  </tbody>
</table>
<button type="button" id="submit">登録</button>
