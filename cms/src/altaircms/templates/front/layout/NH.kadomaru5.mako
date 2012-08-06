## above_kadomaru,kadomaru,below_kadomaru
<%def name="widgets(name)">
  % for w in display_blocks[name]:
      ${w|n}
  % endfor
</%def>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html lang="jp">
<head>
	<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
	<link rel="stylesheet" type="text/css" href="/static/NH/css/style.css" media="all" />
	    <title>${page.title}</title>    <meta name="description" content="${page.description}">    <meta name="keywords" content="${page.keywords}">
</head>
<body>
	<!-- wrapper -->	
	<div class="wrapper">
		<!-- メインカラム -->
		<div class="maincol">
			<header>
				<div class="gnavi">
					<ul>
%for c in myhelper._get_categories(request, "header_menu"):
	<li><a href="${h.link.get_link_from_category(request,c)}">${c.label}</a></li>
%endfor
					</ul>　　
				</div>
			</header>

			  <%block name="above_kadomaru">
                ${widgets("above_kadomaru")}
			  </%block>

			<div class="kadomaru">
			  <%block name="kadomaru">
                ${widgets("kadomaru")}
			  </%block>
			</div>
			<div class="kadomaru">
			  <%block name="kadomaru2">
                ${widgets("kadomaru2")}
			  </%block>
			</div>
			<div class="kadomaru">
			  <%block name="kadomaru3">
                ${widgets("kadomaru3")}
			  </%block>
			</div>
			<div class="kadomaru">
			  <%block name="kadomaru4">
                ${widgets("kadomaru4")}
			  </%block>
			</div>
			<div class="kadomaru">
			  <%block name="kadomaru5">
                ${widgets("kadomaru5")}
			  </%block>
			</div>
			<!-- kadomaru終わり -->

			  <%block name="below_kadomaru">
                ${widgets("below_kadomaru")}
			  </%block>


			<footer>
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
			</footer>

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
