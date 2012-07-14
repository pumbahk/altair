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
	<link rel="stylesheet" type="text/css" href="/static/89ers/css/style.css" media="all" />
	<title>89ers</title>
</head>
<body>
	<!-- wrapper -->	
	<div class="wrapper">
		<!-- メインカラム -->
		<div class="maincol">
			<header>
				<div class="gnavi">
					<ul>
						<li><a href="#">チケットTOP</a></li>
						<li><a href="#">チケット購入・引取方法</a></li>
						<li><a href="#">ブースタークラブ申込</a></li>
						<li><a href="#">よくある質問</a></li>
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
