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

<form id="topcontent_add_form" action="${request.route_path("topcontent_list")}?html=t" method="POST">
  <table class="table">
    <tbody>
      ${formfield("title")}
      ${formfield("kind")}
      ${formfield("publish_open_on")}
      ${formfield("publish_close_on")}
      ${formfield("text")}
      ${formfield("orderno")}
      ${formfield("is_vetoed")}
      ${formfield("image_asset")}
      ${formfield("countdown_type")}
    </tbody>
  </table>
  <button type="submit" class="btn">保存</button>
</form>
