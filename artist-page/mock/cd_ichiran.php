<?php

$dbh = mysql_connect("127.0.0.1:3306", "root", 'root');
mysql_selectdb("artistpage");



//ジャンルないcd一覧
 $cdichiran_cd = "select cdname from cds";
 $cdichiran_cdd = mysql_query($cdichiran_cd,$dbh);
 
 
 echo "<h4>ジャンル別CD一覧</h4>";
  while($row=mysql_fetch_assoc($cdichiran_cdd)){
	echo($row['cdname']);
	echo "<br>";

	}


echo "<br>";






echo "-------------------------------------------------------------------";

?>
<html>
<head>
<link rel="stylesheet" href="artist_top.css" type="text/css" />
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<script type="text/javascript" src="http://www.google.com/jsapi"></script>  
<script type="text/javascript">google.load("jquery", "1.2");</script>
<script type="text/javascript" src="artist_top.js"></script>
</head>
<body>
<div id = "container">
	<div id ="mainbox">
		<div id="page_hanbetu"><p>CD一覧ページ</p></div>
		<div id ="header">
		<ul>
		<a href="artist_top.html"><li>トップへ</li></a>	<a href="#.html"><li>＊＊＊</li></a>	<a href="#.html"><li>＊＊＊</li></a>	<a href="#.html"><li>＊＊＊</li></a>

	</div>
		<div id ="kensaku" >
	
		<form action="http://www.goo.ne.jp/default.asp">
			
			<input type=text name="MT" size=20>
			<input type=submit value="検索" name="act.search">
			<input type="hidden" name="SM" value="MC">
			<input type=hidden name="RD" value="DM">
			<input type=hidden name="Domain" value="www.tohoho-web.com">
			<input type=hidden name="Path" value="">
			<input type=hidden name="from" value="USR">
			<input type=hidden name="DC" value="50">
		</form>
	</div>
	<div id = "tx_left">
			<ul>
				<li id ="#"><a href ="genre.html">jpop</a></li>
				<li id ="#"><a href ="genre.html">洋楽</a></li>
				<li id ="#"><a href ="genre.html">kpop.アジア</a></li>
				<li id ="#"><a href ="genre.html">ワールド</a></li>
				<li id ="#"><a href ="genre.html">レゲエ</a></li>
				<li id ="#"><a href ="genre.html">ロック</a></li>
				<li id ="#"><a href ="genre.html">エレクトロニカ</a></li>
				<li id ="#"><a href ="genre.html">ダンス.ハウス</a></li>
				<li id ="#"><a href ="genre.html">ヒーリング</a></li>
				<li id ="#"><a href ="genre.html">クラシック洋</a></li>
				<li id ="#"><a href ="genre.html">クラシック邦</a></li>
				<li id ="#"><a href ="genre.html">アニメ映画</a></li>
		</ul>
<div id ="left_sec">
				<h6>シーズン>>></h6>
			<a href =""><h5>卒業シーズン　といったらこれな曲</h5></a>
		</div>
		
					<div id ="left_sec">
					<h6>あのCMで流れている曲</h6>
							<ul>

				<li id ="#"><a href ="tokushuu.html">アフラックのアヒルが...</a></li>
				<li id ="#"><a href ="tokushuu.html">札幌ビールCM曲....</a></li>
				<li id ="#"><a href ="tokushuu.html">AKBタイアップ.....</a></li>
				<li id ="#"><a href ="tokushuu.html">Fujizeloxの.....</a></li>
				
		</ul>
		</div>
	</div>
	<div id = "tx_center">
		<div id ="ke"><h5>50音順で選ぶ>>></h5></div>
<form name="selbox">
<select name="league" onchange="TeamSet()">
<option value="">ア行</option>
<option value="">カ行</option>
<option value="">サ行</option>
<option value="">タ行</option>
<option value="">ナ行</option>
<option value="">ハ行</option>
<option value="">マ行</option>
<option value="">ヤ行</option>
<option value="">ラ行</option>
<option value="">ワ行</option>
</select>
</form>
<h6><a href ="gyousentaku.html">で探す</a></h6>




	
	<div id ="tabl">
		<IFRAME src="./i.html" frameborder="1" width="600" height="400">
	

</IFRAME>
</div>


</div>


	
	<div id = "tx_right">
		<!--芸能人のツイッター　日替わり？

<script charset="utf-8" src="http://widgets.twimg.com/j/2/widget.js"></script>
<script>
new TWTR.Widget({
  version: 2,
  type: 'profile',
  rpp: 8,
  interval: 30000,
  width: 170,
  height: 300,
  theme: {
    shell: {
      background: '#31def5',
      color: '#ffffff'
    },
    tweets: {
      background: '#fafafa',
      color: '#050505',
      links: '#3b30d9'
    }
  },
  features: {
    scrollbar: false,
    loop: false,
    live: true,
    behavior: 'all'
  }
}).render().setUser('katosaori').start();
</script>-->


	</div>
	</div>
	</div>
			<!--<div id="footer">
			<div id ="continer">
				<ul>
					<li>
						<a href="">運営について</a>
					</li>
					<li>
						<a href="">ヘルプ</a>
					</li>
					<li>
						<a href="">求人</a>
					</li>
					<li>
						<a href="">規約</a>
					</li>
					<li>
						<a href="">プライバシー</a>
					</li>
					<li>
						<span id="copyright">&copy;2011 ####.</span>
					</li>
				</ul>
			</div>-->
</div>
</body>
</html>
