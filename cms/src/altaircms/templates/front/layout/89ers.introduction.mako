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

<%block name="above_table">
  ${widgets("above_table")}
</%block>


				<table class="info">
					<colgroup width="130px">
					<colgroup width="150px">
					<colgroup width="100px" align="center">
					<colgroup>

					<thead>
						<tr>
							<th>
								支払方法
							</th>
							<th>
								チケット引取方法
							</th>
							<th>
								手数料
							</th>
							<th>
								備考
							</th>
						</tr>
					</thead>
					<tbody>
						<tr>
							<th rowspan="4" class="last">
								クレジットカード
							</th>
							<td>
								QRコード
							</td>
							<td class="textC centerCell">
								無料
							</td>
							<td>
								QRコードを携帯に転送orプリントアウトでOK!　<span class="detail">&raquo; <a href="#"><small>詳しく</small></a></span>
							</td>
						</tr>
						<tr>
							<td>
								セブン-イレブンにて引取
							</td>
							<td class="textC centerCell">
								無料
							</td>
							<td>
								セブン-イレブンの店頭レジにて払込票番号を伝えるだけ!　<span class="detail">&raquo; <a href="#"><small>詳しく</small></a></span>
							</td>
						</tr>
						<tr>
							<td>
								自宅へ配送
							</td>
							<td class="textC centerCell">
								630円/1申込
							</td>
							<td>
								お申込み時に入力頂いた住所へチケットを配送します！　<span class="detail">&raquo; <a href="#"><small>詳しく</small></a></span>
							</td>
						</tr>
						<tr>
							<td>
								当日引き換え
							</td>
							<td class="textC centerCell">
								100円/1枚
							</td>
							<td>
								予約完了メールのプリントアウトをご持参いただき、会場窓口でチケットと引き換え！　<span class="detail">&raquo; <a href="#"><small>詳しく</small></a></span>
							</td>
						</tr>
						<tr>
							<th class="last">
								セブン-イレブン<br />にて支払い
							</th>
							<td>
								その場で発券
							</td>
							<td class="textC centerCell">
								158円/1申込
							</td>
							<td>
								セブン-イレブンの店頭レジにて払込票番号を伝えるだけ!　<span class="detail">&raquo; <a href="#"><small>詳しく</small></a></span>
							</td>
						</tr>
					</tbody>
				</table>

<%block name="below_table">
  ${widgets("below_table")}
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
