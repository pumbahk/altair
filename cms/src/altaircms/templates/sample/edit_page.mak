<%namespace name="layoutcss" file="layouts.css.mak"/>
<%namespace name="block" file="layouts.mak"/>
<%namespace name="css" file="component.css.mak"/>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
  <head>
	<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
    <style type="text/css">
	</style>   
    <link rel="stylesheet" type="text/css" href="/static/css/overlay-basic.css"/>
	<link rel="stylesheet" type="text/css" href="/static/css/my/sample.css">
	<link rel="stylesheet" type="text/css" href="/static/css/my/edit_page.css">
  </head>
  <body>
    <h1>edit page</h1>

	<h2>page info</h2>
    ${h.markup_render(form)}
	<!-- add widget section -->
	<h2>add widget</h2>
	<div id="widget_palet">
		<div id="image_widget" class="widget red float-left">image widget</div>
		<div id="freetext_widget" class="widget blue float-left">freetext widget</div>
		<div id="dummy_widget2"  class="widget green float-left">widget</div>
		<div id="dummy_widget3"  class="widget gray float-left">widget</div>
		<div id="dummy_widget4"  class="widget green float-left">widget</div>
		<div id="dummy_widget5"  class="widget blue float-left">widget</div>
		<div id="dummy_widget6"  class="widget red float-left">widget</div>
	</div>
	
	<div id="selected_layout" class="clear">
      <div id="wrapped">
        % for name  in layout_image:
        <div id="${name}" class="block noitem">${name}</div>
        % endfor
      </div>
	</div>
	
	<div class="dialog_overlay" id="overlay">
	  <!-- the external content is loaded inside this tag -->
	  <div id="wrap" class="contentWrap"></div>
	</div>
	
	<%text>
	<script type="text/html" id="dropped_widget_template">
	  <div class="dropped-widget"><%= name %>
	  </div>
	</script>
    </%text>
<br>
<br>	<br>	<br>
    <script type="text/javascript" src="/static/js/my/widgets/base.js"></script>
    <script type="text/javascript" src="/static/js/my/widgets/image.js"></script>
    <script type="text/javascript" src="/static/js/my/widgets/freetext.js"></script>
    <script type="text/javascript" src="/static/js/my/edit_page.js"></script>
</body>
</html>
