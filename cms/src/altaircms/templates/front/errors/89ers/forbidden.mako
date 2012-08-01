<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html lang="jp">
<head>
	<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
	<link rel="stylesheet" type="text/css" href="/static/89ers/css/style.css" media="all" />
	<title>89ers</title>

	<!--[if lte IE 6]>  
    <script type="text/javascript" src="/static/89ers/js/DD_belatedPNG.js">  
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
<% from altairsite.front import helpers as myhelper %>
%for c in myhelper._get_categories(request, "header_menu"):
	<li><a href="${h.link.get_link_from_category(request,c)}">${c.label}</a></li>
%endfor
					</ul>　　
				</div>
			</div>

			<div class="kadomaru">
ページの閲覧は禁止されています。
			</div>
			<!-- kadomaru終わり -->

			<div class="footer">
				<div class="footernav">
		          <ul>
		            <li class="first"><a href="/static/faq/faq.html">ヘルプ</a></li>
		            <li><a href="http://www.ticketstar.jp/corporate">運営会社</a></li>
		            <li><a href="https://ticket.rakuten.co.jp/contact/form">お問い合わせ</a></li>
		            <li><a href="http://www.ticketstar.jp/privacy">個人情報保護方針</a></li>
		            <li class="last"><a href="http://www.ticketstar.jp/legal">特定商取引法に基づく表示</a></li>
		          </ul>
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
