<%def name="widgets(name)">
  % for w in display_blocks[name]:
      ${w|n}
  % endfor
</%def>

## above_table,below_table,card_and_QR,card_and_seven,card_and_home,card_and_onsite

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html lang="jp">
<head>
	<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
	<link rel="stylesheet" type="text/css" href="/static/NH/css/style.css" media="all" />
	<title>NH</title>
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

			<div class="kadomaru">

<%block name="kadomaru">
  ${widgets("kadomaru")}
</%block>

				<table class="info" style="border-left:1px #ccc solid;">
					<tr>
						<th>クレジットカードでお支払い　＆　QRコードでお引き取り</th>
					</tr>
					<tr>
						<td>
<%block name="card_and_QR">
  ${widgets("card_and_QR")}
</%block>
						</td>
					</tr>
				</table>

				<table class="info" style="border-left:1px #ccc solid;">
					<tr>
						<th>クレジットカードでお支払い　＆　セブン-イレブンにて引取</th>
					</tr>
					<tr>
						<td>
<%block name="card_and_seven">
  ${widgets("card_and_seven")}
</%block>
						</td>
					</tr>
				</table>

				<table class="info" style="border-left:1px #ccc solid;">
					<tr>
						<th>クレジットカードでお支払い　＆　自宅へ配送</th>
					</tr>
					<tr>
						<td>
<%block name="card_and_home">
  ${widgets("card_and_home")}
</%block>
						</td>
					</tr>
				</table>

				<table class="info" style="border-left:1px #ccc solid;">
					<tr>
						<th>セブン-イレブンにてお支払い　＆　その場で発券・引取</th>
					</tr>
					<tr>
						<td>
<%block name="card_and_onsite">
  ${widgets("card_and_onsite")}
</%block>
						</td>
					</tr>
				</table>
				
			</div>



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
