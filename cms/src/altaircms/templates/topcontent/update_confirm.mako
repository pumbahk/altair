<%inherit file='../layout_2col.mako'/>

<div class="row" style="margin-bottom: 9px">
  <h2 class="span6">更新 トピックのタイトル - ${topcontent['title']} (ID: ${topcontent['id']})</h2>
</div>

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


<div class="row">
  <div class="alert alert-info">
	データ更新
  </div>
  <div class="span5">
	<form action="${request.route_path("topcontent", id=topcontent["id"])}" method="POST">
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
 	  <input id="_method" name="_method" type="hidden" value="put" />
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> Update</button>
    </form>
  </div>
</div>
