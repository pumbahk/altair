<%inherit file='../layout_2col.mako'/>
<%namespace name="nco" file="../navcomponents.mako"/>
<%namespace name="fco" file="../formcomponents.mako"/>
<%namespace name="co" file="./components.mako"/>

<%block name='style'>
<style type="text/css">

  .alert{ margin:1%  }
  .size1{ width:84.5%;  }
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

<h2>ページの追加</h2>

<div class="row-fluid">
  <div class="span12">
    ${nco.breadcrumbs(
	    names=[u"Top", u"Page", u"新しいページの追加"],
	    urls=[request.route_path("dashboard"),
              request.route_path("page")]
	)}
  </div>
</div>

<div class="row">
  <div class="span5">
	<h2>ページの初期値設定フォーム</h2>
  </div>
  <div class="span6">
	<h2>layout image</h2>
  </div>
    
  <div class="span6">
	${co.setup_info_form()}
	<h2>form</h2>
	<form id="submit_form" action="${request.current_route_path(action="create")}" method="POST">
     ${fco.form_as_table_strict(form, ["parent", "name", "url", "title", "publish_begin", "publish_end","description","keywords","tags","private_tags","layout"])}
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> Create</button>
    </form>
  </div>
  <div class="span5" id="layout_demo">
  </div>
</div>
