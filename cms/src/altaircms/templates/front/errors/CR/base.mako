## block: header_navigation, footer_navigation
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html lang="jp">
<head>
	<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
	<link rel="stylesheet" type="text/css" href="${request.static_url("altaircms:static/CR/css/style.css")}" media="all" />
	<title>サンレーヴスチケット</title>

	<!--[if lte IE 6]>  
    <script type="text/javascript" src="images/DD_belatedPNG.js">  
    </script>  
    <script type="text/javascript"> DD_belatedPNG.fix( '.header,.sparkle');</script>  
    <![endif]-->  

</head>
<body>
	<!-- wrapper -->	
	<div class="wrapper">
		<!-- メインカラム -->
		<div class="maincol">
			<div class="header">
				<div class="gnavi">
					<ul>
            <%block name="header_navigation">
<%doc>
						<li><a href="top.html">チケットTOP</a></li>
						<li><a href="purchase.html">チケット購入</a></li>
						<li><a href="howto.html">引取方法</a></li>
						<li><a href="faq.html">よくある質問</a></li>
						<li><a href="confirmation.html">購入確認</a></li>
</%doc>
            </%block>
					</ul>　　
				</div>
			</div>
			
			<div class="kadomaru">

				<div class="textC" style="font-size:28px;font-weight:bold;">
    ${next.body()}
        </div>


			</div>



			<div class="footer">
				<div class="footernav">
          <%block name="footer_navigation">
<%doc>
          <ul>
		            <li class="first"><a href="/static/faq/faq.html">ヘルプ</a></li>
		            <li><a href="http://www.ticketstar.jp/corporate">運営会社</a></li>
		            <li><a href="https://ticket.rakuten.co.jp/contact/form">お問い合わせ</a></li>
		            <li><a href="http://www.ticketstar.jp/privacy">個人情報保護方針</a></li>
		            <li class="last"><a href="http://www.ticketstar.jp/legal">特定商取引法に基づく表示</a></li>
</%doc>
		      </ul>
         </%block>
		        </div>
				<div class="copyright">
					Copyright &copy; 2010-2011 TicketStar Inc. All Rights Reserved. 
				</div>
			</div>

		</div>
		<!-- メインカラムおわり -->
		<!-- サイドバー -->
		<div class="sidebar">
			
			
			
		</div>	
		<!-- サイドバーおわり -->
		
	</div>
	<!-- wrapperおわり -->
</body>
</html>
