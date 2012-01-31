<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title><%block name="fulltitle">Ticketstar CMS</%block></title>
    <link rel="shortcut icon" href="/static/favicon.ico" />
    <link rel="stylesheet" type="text/css" href="http://yui.yahooapis.com/3.4.1/build/cssreset/cssreset-min.css" />
    <link rel="stylesheet" href="/static/style.css" type="text/css" media="screen" charset="utf-8" />
    <link rel="stylesheet" href="/static/style-debug.css" type="text/css" media="screen" charset="utf-8" />
    <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
    ## javascript block
    <%block name="js"/>
    <script type="text/javascript">
      ## jQuery depended javascript code
      $(document).ready(function() {
        <%block name="jquery"/>
      });
    </script>
    ## style
    <%block name="style"/>
  </head>
  <body>
    <div id="wrapper">
      <div id="header"><%block name="header"><%include file="parts/header.html"/></%block></div>
      <div id="content"><%block name="content"/>
          ${next.body()}</div>
      <div id="footer"><%block name="footer"><%include file="parts/footer.html"/></%block></div>
    </div>
    ## javascript block
    <%block name="js_foot"/>
  </body>
</html>
