<!DOCTYPE html>
<html>
  <head>
    <title><%block name="fulltitle">Ticketstar CMS</%block></title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <link rel="shortcut icon" href="/static/favicon.ico">
    <link href="/static/bootstrap/css/bootstrap.css" rel="stylesheet">
    <style>
          body {
              padding-top: 60px; /* 60px to make the container go all the way to the bottom of the topbar */
          }
    </style>
    <!-- Le HTML5 shim, for IE6-8 support of HTML5 elements -->
    <!--[if lt IE 9]>
    <script src="//html5shim.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->

    <%doc>
    <link rel="stylesheet" type="text/css" href="http://yui.yahooapis.com/3.4.1/build/cssreset/cssreset-min.css">
    <link rel="stylesheet" href="/static/style.css" type="text/css" media="screen" charset="utf-8">
    <link rel="stylesheet" href="/static/style-debug.css" type="text/css" media="screen" charset="utf-8">
    </%doc>
    <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
    <script type="text/javascript" src="/static/bootstrap/js/bootstrap.js"></script>
    ## javascript block
    <%block name="js"/>
    <script type="text/javascript">
      ## jQuery depended javascript code
      $(document).ready(function() {
            $().dropdown();
            <%block name="jquery"/>
      });
    </script>
    ## style
    <%block name="style"/>
  </head>
  <body>
    <%block name="header"><%include file="parts/header.html"/></%block>
    <div class="container row-fluid">
      <%block name="content"/>${next.body()}
      <%block name="footer"><%include file="parts/footer.html"/></%block>
    </div>


    ## javascript block
    <%block name="js_foot"/>
  </body>
</html>
