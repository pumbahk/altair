<%def name="alert(css_kls, messages)">
  %if messages:
	<div class="${css_kls}">
	  <a class="close" data-dismiss="alert">×</a>
	  %for mes in messages:
		<p>${mes}</p>
	  %endfor
   </div>
 %endif
</%def>

<div class="flashmessage">
  ${alert("alert alert-block alert-success",   request.session.pop_flash("successmessage"))}
  ${alert("alert alert-block alert-info",   request.session.pop_flash("infomessage"))}
  ${alert("alert alert-block alert-error", request.session.pop_flash("errormessage"))}
</div>
