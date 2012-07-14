## kadomaru
<%def name="widgets(name)">
  % for w in display_blocks[name]:
      ${w|n}
  % endfor
</%def>

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
						<li><a href="#">チケット購入・引取方法</a></li>
						<li><a href="#">入場方法</a></li>
						<li><a href="#">ファンクラブ申し込みフォーム</a></li>
						<li><a href="#">よくある質問</a></li>
					</ul>　　
				</div>
			</header>

			<div class="kadomaru">
			  <%block name="kadomaru">
                ${widgets("kadomaru")}
			  </%block>
			</div>
			<!-- kadomaru終わり -->



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
