<%block name="page">
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <title>simlple</title>
	<%block name="js_prerender"/>
    <script type="text/javascript">
    $(function(){<%block name="js_postrender"/>);
    </script>
  </head>
  <body>
	<div id="header">
	  <h2>header</h2>
	  <%block name="header">header</%block>
	</div>
	<div id="content">
	  <h2>content</h2>
	  <%block name="content">content</%block>
	</div>
	<div id="footer">
	  <h2>footer</h2>
	  <%block name="footer">footer</%block>
	</div>
  </body>
</html>
</%block>
