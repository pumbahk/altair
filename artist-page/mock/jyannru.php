<?php


$dbh = mysql_connect("127.0.0.1:3306", "root", 'root');
mysql_selectdb("artistpage");
//ランキング

$atop_rank ="select * from ranking";
$atop_rankk = mysql_query($atop_rank,$dbh);
$atop_rankkout = mysql_fetch_assoc($atop_rankk);
$atop_rankkoutar = mysql_fetch_row($atop_rankk);
echo "<h4>ランキング</h4>";
echo "<br>";
 foreach($atop_rankkoutar as $value){
	 print $value;
	 	 echo "　　　";

	 }
	 
	 
echo "<br>";

 foreach($atop_rankkout as $value){
	 print $value;
	 echo "　　　";
	 }	
echo "<br>";
	 
//最新リリース

$release= "SELECT * FROM cds
WHERE release_date BETWEEN
between date_add(date(now()), interval -6 day) and date_format(now(), '%Y.%m.%d')
ORDER BY release_date";
$release_test = "select * from cds";

$test = mysql_query($release_test,$dbh);
echo $test;
echo "<h4>最新リリース</h4>";

$releasee = mysql_query($release,$dbh);
$releaseeout = mysql_fetch_assoc($releasee);
$releaseeoutar = mysql_fetch_row($releasee);
foreach($releaseeoutar as $value){
	echo $value;
	}
	
	echo "<br>";


//ライブコンサート情報

$atop_live = "select * from event";
$live = mysql_query($atop_live,$dbh);
$livear = mysql_fetch_assoc($live);
echo "<h4>ライブコンサート情報<h4>";
echo $livear;
echo "<br>";
while($row=mysql_fetch_assoc($live)){
	echo($row['about']);
	echo "      ";
	echo($row['genre']);
	echo "      ";
	echo($row['date']);
	echo"        ";
	echo "<br>";

	}


echo "----------------------------------------------------------------------";	

?>
<html>
<head>
<link rel="stylesheet" href="jyannru.css" type="text/css" />
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<script type="text/javascript" src="http://www.google.com/jsapi"></script>  
<script type="text/javascript">google.load("jquery", "1.2");</script>
<script type="text/javascript" src="jyannru.js"></script>
</head>
<body>
<div id = "container">
	<div id ="mainbox">
		<div id="page_hanbetu">＊＊＊ジャンル選択あと</div>
		<div id ="header">
			<ul>
			<a href="artist_top.html"><li>トップへ</li></a>	<a href="#.html"><li>＊＊＊</li></a>	<a href="#.html"><li>＊＊＊</li></a>	<a href="#.html"><li>＊＊＊</li></a>	
			</ul>

		</div>
		<div id ="kensaku" >
	
			<form action="http://www.goo.ne.jp/default.asp">
				<a href="http://www.goo.ne.jp"></a>
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
				<li id ="#"><a href ="cd_ichiran.html">pop</a></li>
				<li id ="#"><a href ="cd_ichiran.html">演歌</a></li>
				<li id ="#"><a href ="cd_ichiran.html">アイドル</a></li>
				<li id ="#"><a href ="cd_ichiran.html">シンガーソングライター</a></li>
				<li id ="#"><a href ="cd_ichiran.html">昭和歌謡</a></li>
				<li id ="#"><a href ="cd_ichiran.html">エレクトロ二カ</a></li>
				<li id ="#"><a href ="cd_ichiran.html">インディーズ</a></li>
				<li id ="#"><a href ="cd_ichiran.html">カラオケ人気</a></li>
				<li id ="#"><a href ="cd_ichiran.html">アニメ</a></li>
				<li id ="#"><a href ="cd_ichiran.html">CM曲</a></li>
				<li id ="#"><a href ="cd_ichiran.html">映画</a></li>
				<li id ="#"><a href ="cd_ichiran.html">なにかしらのグループ</a></li>
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
		
			<div id =" top_news" >
				

					
					<IFRAME src="./r.html" frameborder="1" width="300" height="400">
	

</IFRAME>
					
									
					
						<div id ="live">
							<p>ライブ.コンサート情報</p><p class = "next_news">
								<a href ="live_info.html"><h6>もっとみる>>></h6></a></p>

							<div id ="live_info">
								
								<p class ="tit">JUJUライブin武道館</p>
								<p>JUJUが一年ぶりの全国ツアーJUJUが一年ぶりの全国ツアーJUJUが一年ぶりの全国ツアーJUJUが一年ぶりの全国ツアーJUJUが一年ぶりの全国ツアーJUJUが一年ぶりの全国ツアーJUJUが一年ぶりの全国ツアーJUJUが一年ぶりの全国ツアーJUJUが一年ぶりの全国ツアー</p>
							</div>
							<div id ="live_info">
								<p class ="tit">JUJUライブin武道館</p>
								<p>JUJUが一年ぶりの全国ツアーJUJUが一年ぶりの全国ツアーJUJUが一年ぶりの全国ツアーJUJUが一年ぶりの全国ツアーJUJUが一年ぶりの全国ツアーJUJUが一年ぶりの全国ツアーJUJUが一年ぶりの全国ツアーJUJUが一年ぶりの全国ツアーJUJUが一年ぶりの全国ツアー</p>
							</div>
							<div id ="live_info">
								<p class ="tit">JUJUライブin武道館</p>
								<p>JUJUが一年ぶりの全国ツアーJUJUが一年ぶりの全国ツアーJUJUが一年ぶりの全国ツアーJUJUが一年ぶりの全国ツアーJUJUが一年ぶりの全国ツアーJUJUが一年ぶりの全国ツアーJUJUが一年ぶりの全国ツアーJUJUが一年ぶりの全国ツアーJUJUが一年ぶりの全国ツアー</p>
							</div>
						</div>
					</div>
					
						
						
						
						<div id ="sinpu">
							<h3>リリース情報</h3>
							<div id="sinpu_s">
								<img src="./img/2.png" alt = "photo" width = 50 height =50>
								<p><h6>何月何日リリース だれだれ　なになに</h6></p></div>
							
							<div id="sinpu_s">
									<img src="./img/2.png" alt = "photo" width = 50 height =50>
									<p><h6>何月何日リリース だれだれ　なになに</h6></p>
							</div>
							<div id="sinpu_s">
									<img src="./img/2.png" alt = "photo" width = 50 height =50>
									<p><h6>何月何日リリース だれだれ　なになに</h6></p>
							</div>
							<div id="sinpu_s">
									<img src="./img/2.png" alt = "photo" width = 50 height =50>
									<p><h6>何月何日リリース だれだれ　なになに</h6></p>
							</div>
							<div id="sinpu_s">
									<img src="./img/2.png" alt = "photo" width = 50 height =50>
									<p><h6>何月何日リリース だれだれ　なになに</h6></p>
							</div>
							<div id="sinpu_s">
									<img src="./img/2.png" alt = "photo" width = 50 height =50>
									<p><h6>何月何日リリース だれだれ　なになに</h6></p>
							</div>
							<div id="sinpu_s">
									<img src="./img/2.png" alt = "photo" width = 50 height =50>
									<p><h6>何月何日リリース だれだれ　なになに</h6></p>
							</div>
							<div id="sinpu_s">
									<img src="./img/2.png" alt = "photo" width = 50 height =50>
									<p><h6>何月何日リリース だれだれ　なになに</h6></p>
							</div>
							<div id="sinpu_s">
									<img src="./img/2.png" alt = "photo" width = 50 height =50>
									<p><h6>何月何日リリース だれだれ　なになに</h6></p>
							</div>
						</div>
					</div>
				</div>

		

	<div id = "tx_right">
		<!--このジャンルに関する　ツイートを表示できたr
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
