<%inherit file='../layout_2col.mako'/>

<%block name='style'>
<style type="text/css">
  .alert{ margin:1%  }
  .size1{ width:100%;  }
  .size2{ width:34.5%; }
  .size3{ width:17.8%; }
  .left{ float:left; }
  .clear{ clear:both; }
</style>
</%block>

<script type="text/javascript">
  var render_demo = function(){
    var layout_id = $(this).val();
    $("#layout_demo").load("${request.route_path("layout_demo")}"+"?id="+layout_id);
  };

  $(function(){
    $("[name='layout']").live("change", render_demo);
    render_demo.call($("[name='layout']"));
  });
</script>

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


<div class="row">
  <div class="span5">
	<h2>form</h2>
  </div>
  <div class="span5">
	<h2>layout image</h2>
  </div>
  <div class="span5">
	<form action="${request.route_path("page_add",event_id=event.id)}" method="POST">
      <table class="table">
        <tbody>
          ${formfield("title")}
          ${formfield("event")}
          ${formfield("parent")}
          ${formfield("url")}
          ${formfield("description")}
          ${formfield("keywords")}
          ${formfield("tags")}
          ${formfield("private_tags")}
          ${formfield("layout")}
        </tbody>
      </table>
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> Create</button>
    </form>
  </div>
  <div class="span5" id="layout_demo">
  </div>
</div>
