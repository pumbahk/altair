<!DOCTYPE html>
<html>
  <head>
    <title><%block name="fulltitle">Ticketstar CMS</%block></title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="shortcut icon" href="/static/favicon.ico">
    <style>
          body {
              padding-top: 60px; /* 60px to make the container go all the way to the bottom of the topbar */
          }
    </style>
	## for date picker
	<link rel="stylesheet" type="text/css" href="/static/css/datepicker.css"/>
	<script type="text/javascript" src="/static/js/bootstrap-datepicker.js"></script>
    ## style
    <%block name="style"/>
  </head>
  <body>
    <%block name="header"><%include file="parts/header.mako"/></%block>
    <div class="container">
      <%block name="content"/>${next.body()}
      <%block name="footer"><%include file="parts/footer.mako"/></%block>
    </div>

    ## javascript block
    <!-- Le HTML5 shim, for IE6-8 support of HTML5 elements -->
    <!--[if lt IE 9]>
    <script src="//html5shim.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->
    <%doc> <script type="text/javascript" src="/static/bootstrap/js/bootstrap.js"></script> </%doc>
    ## javascript block
    <%block name="js"/>
    <script type="text/javascript">
      ## jQuery depended javascript code
      $(document).ready(function() {
            $().dropdown();
	        $(".datepicker").datepicker({
	           weekStart: 1,
	           format: "yyyy-mm-dd HH:MM:SS"
	        }).on("changeDate", function(){
              alert(ev.date);
            });
            <%block name="jquery"/>
      });
    </script>
    <%block name="js_foot"/>
  </body>
</html>
