<%inherit file='../layout_2col.mako'/>
<%namespace name="nco" file="../navcomponents.mako"/>
<%namespace name="fco" file="../formcomponents.mako"/>
<%namespace name="mco" file="../modelcomponents.mako"/>

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

<h2>ページの追加(event: ${event.title})</h2>

<div class="row-fluid">
  <div class="span10">
    ${nco.breadcrumbs(
	    names=["Top", "Event", event.short_title, u"新しいページの追加"], 
	    urls=[request.route_path("dashboard"),
              request.route_path("event_list"),
              request.route_path("event", id=event.id)]
	)}
  </div>
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

     ${fco.form_as_table_strict(form, ["url", "add_to_pagset", "pageset","title","event", "publish_begin", "publish_end", "parent","description","keywords","tags","private_tags","layout"])}
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> Create</button>
    </form>
  </div>
  <div class="span5" id="layout_demo">
  </div>
</div>
