<%inherit file='../layout_2col.mako'/>

<div class="row" style="margin-bottom: 9px">
  <h2 class="span6">更新 トピックのタイトル - ${topic['title']} (ID: ${topic['id']})</h2>
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
	<form action="${request.route_path("topic", id=topic["id"])}" method="POST">
      <table class="table">
        <tbody>
          ${formfield("title")}
          ${formfield("kind")}
          ${formfield("publish_at")}
          ${formfield("text")}
        </tbody>
      </table>
 	  <input id="_method" name="_method" type="hidden" value="put" />
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> Update</button>
    </form>
  </div>
</div>
