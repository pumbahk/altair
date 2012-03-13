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

<form id="topic_add_form" action="${request.route_url("topicdialog")}" method="POST">
  <table class="table">
    <tbody>
      ${formfield("topic")}
    </tbody>
  </table>
  <button type="submit" class="btn">保存</button>
</form>
