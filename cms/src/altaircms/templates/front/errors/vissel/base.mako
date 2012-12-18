<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html lang="jp">
<head>
    <meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
    <link rel="stylesheet" type="text/css" href="${request.static_url("altaircms:static/vissel/css/style.css")}" media="all" />
    <title>${page.title}</title>
  <meta name="description" content="${page.description}">
  <meta name="keywords" content="${page.keywords}">
    <!--[if lte IE 6]>  
    <script type="text/javascript" src="/static/vissel/js/DD_belatedPNG.js">  
    </script>  
    <script type="text/javascript"> DD_belatedPNG.fix( '.header,.sparkle');</script>  
    <![endif]-->  
</head>
<body>
    <div class="header">
        <div class="header-inner">
            <img src="images/logo.gif" alt="VISSEL TICKET" />
            <div class="gnavi">
                <a href="" class="historybtn">購入履歴の確認</a><br />
                <ul>
            <%block name="header_navigation">
            </%block>
                </ul>　　
            </div>
        </div>
    </div>

    <!-- wrapper -->    
    <div class="wrapper">
			<div class="kadomaru">
				<div class="textC" style="font-size:28px;font-weight:bold;">
    ${next.body()}
        </div>
			</div>
      <!-- kadomaru終わり -->
    </div>
    <!-- wrapperおわり -->


<div class="footer">
    <div class="footer-inner">
        <img src="images/tomoni.gif" alt="" />
            <div class="footernav">
          <%block name="footer_navigation">
         </%block>
            </div>
        <div class="copyright">
            Copyright &copy; 2010-2011 TicketStar Inc. All Rights Reserved. 
        </div>
    </div>
</div>
</body>
</html>
