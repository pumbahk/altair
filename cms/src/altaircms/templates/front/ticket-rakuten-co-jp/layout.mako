<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <title><%block name="fulltitle">Ticketstar CMS Front End (PC view)</%block></title>
    <meta name="description" content="<%block name="description"/>">
    <meta name="keywords" content="<%block name="keyword"/>">
    <meta http-equiv="Content-Style-Type" content="text/css">
    <meta http-equiv="Content-Script-Type" content="text/javascript">
    <link rel="shortcut icon" href="/static/favicon.ico"/>
    <link rel="stylesheet" type="text/css"
          href="http://rakuten-ticket-static.s3.amazonaws.com/public/stylesheets/default.css"/>
    <link rel="stylesheet" type="text/css"
          href="http://rakuten-ticket-static.s3.amazonaws.com/public/stylesheets/ui-lightness/jquery-ui-1.8.13.custom.css"/>
    <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
    <script type="text/javascript" src="/static/swfobject.js"></script>
    ## javascript block
    <%block name="js"/>
    <script type="text/javascript">
            ## jQuery depended javascript code
                  $(document).ready(function () {
            <%block name="jquery"/>
        });
    </script>
    ## style
    <%block name="style"/>
</head>
<body>
<div class="page page-two_columns">
    <%block name="page"><%include file="../parts/header.mako"/></%block>

    <div class="page-main">
        <div class="page-main-header">
            <div class="page-main-header-content"></div>
        </div>
        <div class="page-main-main">
            <div class="page-main-main-content"><%block name="content"/>${next.body()}</div>
        </div>
        <div class="page-main-footer">
            <div class="page-main-footer-content"></div>
        </div>
    </div>

    <div class="page-footer">
        <div class="page-footer-content"><%block name="footer"><%include file="../parts/footer.mako"/></%block></div>
    </div>

    ## javascript block
    <%block name="js_foot"/>
</div>
</body>
</html>
