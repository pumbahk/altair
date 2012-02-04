<%namespace name="layoutcss" file="layouts.css.mak"/>
<%namespace name="block" file="layouts.mak"/>
<%namespace name="css" file="component.css.mak"/>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
  <head>
    <style type="text/css">

      ${layoutcss.col2A()}
      ${layoutcss.col3A()}
      ${css.colors()}
      ${css.control()}
      #wrapped1 {
      margin: 30px;
      float: left;
      }

      #wrapped2 {
      margin: 30px;
      float: left;
      }

      .dropped-widget {
      width: 100%;
      height: 100px;
	  width:auto;
      background-color: #ffffaa;
      }
    </style>   

    <script type="text/javascript" src="/static/js/my/old_layouts.js"></script>
    <script type="text/javascript" src="/static/js/my/old_sample_api.js"></script>
    <script type="text/javascript" src="/static/js/my/old_sample_manager.js"></script>
    <script type="text/javascript" src="/static/js/my/reaction.js"></script>
    <script type="text/javascript" src="/static/js/my/service.js"></script>
    <script type="text/javascript" src="/static/js/my/sample.js"></script>

    <link rel="stylesheet" type="text/css" href="/static/css/overlay-basic.css"/>
	<link rel="stylesheet" type="text/css" href="/static/css/my/sample.css">
  </head>
  <body>
	<div id="triggers">
      <div id="selected" rel="#peace1">
		<div id="wrapped" class="hidden">
		  ${block.col2A(prefix="selected")}
		</div>
      </div>
    </div>
	
	<div class="simple_overlay" id="peace1">
      <div name="col2A" id="wrapped1" class="candidate">
		${block.col2A(prefix="X")}
      </div>
      <div name="col3A" id="wrapped2" class="candidate">
		${block.col3A(prefix="Y")}
      </div>
	</div>

	<!-- add widget section -->
	<div class="clear">
	  <h2>add widget</h2>
	  <div id="widget_palet">
		<div id="image_widget" class="widget red float-left">image widget</div>
		<div id="dummy_widget1" class="widget blue float-left">widget</div>
		<div id="dummy_widget2" class="widget green float-left">widget</div>
		<div id="dummy_widget3"  class="widget gray float-left">widget</div>
		<div id="dummy_widget4"  class="widget green float-left">widget</div>
		<div id="dummy_widget5"  class="widget blue float-left">widget</div>
		<div id="dummy_widget6"  class="widget red float-left">widget</div>
	  </div>

	  <div id="selected_layout" class="clear">
	  </div>

	  <div class="dialog_overlay" id="overlay">
		<!-- the external content is loaded inside this tag -->
		<div class="contentWrap"></div>
	  </div>
	</div>
  </body>
</html>
