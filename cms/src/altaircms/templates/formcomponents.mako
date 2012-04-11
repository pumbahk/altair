<%def name="form_to_table(form)">
<table class="table table-striped">
  <tbody>
  % for k,v in form.data.iteritems():
    <tr>
	  <td>${getattr(form,k).label}</td>
	  <td>${v}</td>
	</tr>
  % endfor
  </tbody>
</table>
</%def>

<%def name="formfield(form, k)">
	<tr><th>${getattr(form,k).label}</th><td>${getattr(form,k)}
	%if k in form.errors:
	  <br/>
	  %for error in form.errors[k]:
		<span class="btn btn-danger">${error}</span>
	  %endfor
	%endif
	</td></tr>
</%def>
