<%inherit file='../layout_2col.mako'/>
<%namespace name="nco" file="../navcomponents.mako"/>
<%namespace name="fco" file="../formcomponents.mako"/>
<%namespace name="mco" file="../modelcomponents.mako"/>
<%namespace name="co" file="./components.mako"/>

<%block name='style'>
<style type="text/css">
  .alert{ margin:1%  }
  .size1{ width:81%;  }
  .size2{ width:31%; }
  .size3{ width:14.3%; }
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
	${co.setup_info_form()}

	<form id="submit_form" action="#" method="POST">
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
    ${fco.form_as_table_strict(form, ["parent","url", "name","add_to_pagset", "pageset","title", "publish_begin", "publish_end","description","keywords","tags","private_tags","layout"])}
	<button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> 保存</button>
	</form>
  </div>
  <div class="span4" id="layout_demo">
  </div>
</div>

<div class="row-fluid">
  <h4>ページ一覧</h4>
<%
seq = h.paginate(request, pages, item_count=pages.count())
%>
  ${seq.pager()}
  ${mco.model_list(seq.paginated(), mco.page_list, u"ページは登録されていません")}
  ${seq.pager()}
</div>
