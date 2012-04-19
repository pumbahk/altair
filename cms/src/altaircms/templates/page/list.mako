<%inherit file='../layout_2col.mako'/>
<%namespace name="nco" file="../navcomponents.mako"/>
<%namespace name="fco" file="../formcomponents.mako"/>
<%namespace name="mco" file="../modelcomponents.mako"/>

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

<h2>page</h2>

<div class="row-fluid">
  <div class="span10">
    ${nco.breadcrumbs(
	    names=["Top", "Page"], 
	    urls=[request.route_path("dashboard")]
	)}
  </div>
</div>

<div class="row">
  <div class="span5">
	<h4>ページ追加</h4>
  </div>
  <div class="span5">
	<h4>layout image</h4>
  </div>
  <div class="span5">
	<form action="#" method="POST">
	  <script>
	    $(function() {
               var on_add_to_pageset_clicked = function() {
	           if ($('#add_to_pagset').attr('checked')) {
                       $('#url').attr('disabled', 'disabled');
                       $('#pageset').attr('disabled', null);
                   } else {
                       $('#pageset').attr('disabled', 'disabled');
                       $('#url').attr('disabled', null);
                   }
	       };
	       $('#add_to_pagset').click(on_add_to_pageset_clicked);
               on_add_to_pageset_clicked();
	    })
	  </script>
    ${fco.form_as_table_strict(form, ["url", "add_to_pagset", "pageset","title", "publish_begin", "publish_end", "parent","description","keywords","tags","private_tags","layout"])}
	<button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> 保存</button>
	</form>
  </div>
  <div class="span4" id="layout_demo">
  </div>
</div>

<div class="row-fluid">
  <h4>ページ一覧</h4>
  ${mco.model_list(pages, mco.page_list, u"ページは登録されていません")}
</div>
