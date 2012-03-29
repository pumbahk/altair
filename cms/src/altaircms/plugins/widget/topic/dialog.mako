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
<p>(手抜き：本当は画像つき・画像なしとで選択できるトピックの種類を絞り込む必要がある)</p>
<table class="table">
  <tbody>
    ${formfield("topic_type")}
    ${formfield("kind")}
    ${formfield("display_count")}
    ${formfield("display_global")}
    ${formfield("display_page")}
    ${formfield("display_event")}
  </tbody>
</table>
<button type="button" id="submit">登録</button>
