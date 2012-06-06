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
	<h2>ページの初期値設定フォーム</h2>
  </div>
  <div class="span5">
	<h2>layout image</h2>
  </div>
    
  <div class="span5">
	<script type="text/javascript">
	  var propagate_data = function(data){
		var root = $("form#submit_form");
		root.find("input[name='name']").val(data.name);
		root.find("textarea[name='url']").val(data.url);
		root.find("textarea[name='title']").val(data.title);
		root.find("textarea[name='keywords']").val(data.keywords);
		root.find("textarea[name='description']").val(data.description);

	    //$('label[for="url"]').text(data.jurl);

		var parent_field = root.find("select[name='parent']");
		if(data.parent){
	      parent_field.val(data.parent).removeAttr("disabled");
		} else {
	      parent_field.attr("disabled","disabled");
	    }
	  }
	  
	  var propagete_setup_info = function(){
	    var root = $("form#setup_form");
	    var params = {"name": root.find("input[name='name']").val(),
	                  "parent": root.find("select[name='parent']").val()};
		$.getJSON("${request.route_path("api_page_setup_info")}",params).done(function(data,status,req){
		  if (data.error){
			alert(data.error);
		  } else {
	        propagate_data(data);
	  	    console.log(data);
		  }
		}).fail(function(data){console.log(data)})
	    return false; // kill propagation
	  };
	</script>
	<form id="setup_form" onSubmit="return propagete_setup_info();">
     ${fco.form_as_table_strict(setup_form, ["parent", "name"])}
	 <input type="submit" value="初期値をフォームに反映">

	</form>

	<h2>form</h2>
	<form id="submit_form" action="${request.route_path("page_add",event_id=event.id)}" method="POST">
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

     ${fco.form_as_table_strict(form, ["parent", "name", "url", "add_to_pagset", "pageset","title","event", "publish_begin", "publish_end","description","keywords","tags","private_tags","layout"])}
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> Create</button>
    </form>
  </div>
  <div class="span5" id="layout_demo">
  </div>
</div>
