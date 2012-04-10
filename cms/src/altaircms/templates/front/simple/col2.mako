<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
  <head>
	<style type="text/css">
	  body {
	  margin: 0;
	  padding: 0;
	  }

	  #wrapper {
	  width: 900px;
	  margin-left: auto;
	  margin-right: auto;
	  }

	  #header {
	  height: 200px;
	  }
	  #footer {
	  height: 200px;
	  }
	  #col-left {
	  width: 600px;
	  float: left;
	  }
	  #col-right {
	  width: 300px;
	  float: left;
	  }
	  .clear {
	  clear: both;
	  }
	  .gray {
	  background-color: #dddddd;
	  }
	  .blue {
	  background-color: #aaaaff;
	  }
	  .red {
	  background-color: #ffaaaa;
	  }
	</style>
	<%block name="css_prerender"/>
	<%block name="js_prerender"/>
	<script type="text/javascript">
	  $(function(){  <%block name="js_postrender"/>   });
	</script>
  </head>
  <body>
	<div id="wrapper">
	  <div id="header" class="gray">
		header block
		<%block name="header"/>
	  </div>
	  <div id="col-left" class="blue">
		left column
		<%block name="left"/>
	  </div>
	  <div id="col-right" class="red">
		right column
		<%block name="right"/>
	  </div>
	  <div class="clear"></div>
	  <div id="footer" class="gray">
		footer block
		<%block name="footer"/>
	  </div>
	</div>
  </body>
</html>

