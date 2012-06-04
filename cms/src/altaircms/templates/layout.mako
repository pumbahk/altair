<%namespace name="nco" file="./navcomponents.mako"/>

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
		// header css
		#navigation { height:25px; }
		#navigation ul{ list-style-type: none; padding-top:17px; font-size:11px; }
		#navigation ul li{ float:left; display:inline; margin-right:5px;}
		#navigation ul li a,
		#navigation ul li a span { float:left; display:inline; height:25px; padding:0 0 0 8px; background:url(/static/img/nav.gif) no-repeat 0 0; }
		#navigation ul li a span { padding:0 8px 0 0; background-position:right 0; }
		#navigation ul li a { color:#ddadab; line-height:29px;}
		#navigation ul li a.active { font-weight: bold;}

		#navigation ul li a:hover,
		#navigation ul li a.active { background-position:0 bottom; color:#887e42; }

		#navigation ul li a:hover span,
		#navigation ul li a.active span{ background-position:right bottom; }
    </style>
	## for date picker
	<link rel="stylesheet" type="text/css" href="/static/css/datepicker.css"/>
	<script type="text/javascript" src="/static/js/bootstrap-datepicker.js"></script>
    ## style
    <%block name="style"/>
  </head>
  <body>
    <%block name="header">${nco.header()}</%block>
    <div class="container">
      <%block name="content"/>${next.body()}
      <%block name="footer">${nco.footer()}</%block>
    </div>

    ## javascript block
    <!-- Le HTML5 shim, for IE6-8 support of HTML5 elements -->
    <!--[if lt IE 9]>
    <script src="//html5shim.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->
    ## javascript block
    <%block name="js"/>
    <script type="text/javascript">
      ## jQuery depended javascript code
      $(document).ready(function() {
            //$().dropdown();
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
