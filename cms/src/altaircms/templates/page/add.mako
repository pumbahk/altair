<%inherit file='../layout_2col.mako'/>


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

<div class="row" style="margin-bottom: 9px">
  <h2 class="span6">ページの追加</h2>
</div>

<h2>event</h2>
<div>
  ${event.title}
</div>

<h2>form</h2>

<div class="row">
  <div class="span5">
	<form action="${request.route_path("page_add",event_id=event.id)}" method="POST">
      <table class="table">
        <tbody>
          ${formfield("title")}
          ${formfield("url")}
          ${formfield("description")}
          ${formfield("keywords")}
          ${formfield("tags")}
          ${formfield("layout")}
          ${h.base.hidden_input("event_id", event.id)|n}
        </tbody>
      </table>
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> Create</button>
    </form>
  </div>
</div>
