## topic widget dialog
##  view function is views.TopicWidgetView.dialog
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
  <h1>トピック(info)</h1>
</div>

<table class="table">
  <tbody>
    ${formfield("kind")}
    ${formfield("count_items")}
    ${formfield("display_global")}
    ${formfield("display_page")}
    ${formfield("display_event")}
  </tbody>
</table>
<button type="button" id="submit">登録</button>
