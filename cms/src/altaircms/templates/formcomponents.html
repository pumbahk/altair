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

<%def name="form_as_table_strict(form, keys)">
<table class="table table-striped">
  <tbody>
  % if form.errors.get("__all__"):
	<div class="btn btn-danger">
        %for err in form.errors["__all__"]:
          ${err}
        %endfor
    </div>
  % endif

  % for k in keys:
    ${formfield(form, k)}
  % endfor
  </tbody>
</table>
</%def>

<%def name="label_with_required_mark(field)">
  %if field.flags.required:
    <%
      field.label.text += "*"
     %>
  %endif

 ${field.label}
</%def>

<%def name="postdata_as_hidden_input(postdata)">
  % for k,v in postdata.items():
	<input type="hidden" name="${k}" value="${v}">
  % endfor
</%def>

<%def name="formfield(form, k)">
    <%
      field = getattr(form,k)
    %>

	<tr><th>${label_with_required_mark(field)}</th><td>${field}
	%if k in form.errors:
	  <br/>
	  %for error in form.errors[k]:
		<span class="btn btn-danger">${error}</span>
	  %endfor
	%endif
	</td></tr>
</%def>
