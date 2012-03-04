<?php

$dbh = mysql_connect("127.0.0.1:3306", "root", 'root');
mysql_selectdb("artistpage");



//アーティストプロフィール
 $atop_prof = "select prof from artist";
 $atop_proff = mysql_query($atop_prof,$dbh);
 $atop_proffout = mysql_fetch_assoc($atop_proff);
 
 
 echo "<h4>アーティストプロフィール</h4>";
  while($row=mysql_fetch_assoc($atop_proff)){
	echo($row['prof']);
	echo "<br>";

	}


echo "<br>";





//アーティストのリリースcd
echo "<h4>アーティストリリースCD</h4>";
echo "<br>";

$cdshosai_cds = "select cds.cdname from cd_artist inner join cds on cd_artist.cds_id = cds.id where artist_id =2";
$cdshosai_cdss = mysql_query($cdshosai_cds,$dbh);
$cdshosai_releasecd ="select * from cds WHERE release_date BETWEEN (CURDATE() - INTERVAL 7 DAY) AND (CURDATE() + INTERVAL 1 DAY)";

$cdshosai_releasecdd = mysql_query($cdshosai_releasecd,$dbh);
  while($row=mysql_fetch_assoc($cdshosai_releasecdd)){
	echo($row['cdname']);
	echo "<br>";

	}

  while($row=mysql_fetch_assoc($cdshosai_cdss)){
	echo($row['cdname']);
	echo "<br>";

	}



//ジャンル

$atop_genre = "select genre from cds group by genre";
$atop_genree = mysql_query($atop_genre,$dbh);
$atop_genreeout = mysql_fetch_assoc($atop_genree);
$atop_genreeoutar = mysql_fetch_row($atop_genree);

echo "<h4>ジャンル選択枝</h4>";

while($row=mysql_fetch_assoc($atop_genree)){
	echo($row['genre']);
	echo "<br>";

	}

foreach($atop_genreeout as $value){
	print $value;
	}
	echo "<br>";



//楽天ブックスから



echo "<h4>楽天ブックスから曲目 リリース日時</h4>";

$xml_str = file_get_contents('http://api.rakuten.co.jp/rws/3.0/rest?developerId=12657057e6e263dfe5dd57b5565078da&operation=BooksCDSearch&version=2011-12-01&artistName=globe');

 $ret = preg_match('/title/', $xml_str, $match);
    if ($ret == 0) {
      echo('マッチしませんでした。<br/>');
    } else {
      for ($i = 0; $i < count($match); $i++) {
        echo($match[$i] . '<br/>' . "\n");
      }
    }
	
echo "hello";
$xml_str = str_replace('header:Header', 'Header', $xml_str);
$xml_str = str_replace('booksCDSearch:BooksCDSearch xmlns:booksCDSearch="http://api.rakuten.co.jp/rws/rest/BooksCDSearch/2011-12-01"', 'booksCDSearch', $xml_str);
$xml_str = str_replace('booksCDSearch:BooksCDSearch', 'booksCDSearch', $xml_str);

$xml  = simplexml_load_string($xml_str);
//var_dump($xml->Body->booksCDSearch->Items->Item[3]->title);
//var_dump($xml->Body->booksCDSearch->Items->Item[4]->title);

//echo $xml->Body->booksCDSearch->Items->Item[3]->title;

echo "\n";

for ($x=0;$x<=9;$x++){
	echo $xml->Body->booksCDSearch->Items->Item[$x]->title."--------".$xml->Body->booksCDSearch->Items->Item[$x]->salesDate;
;
	echo "<br>";
	}
	
echo "<br>";

echo "<br>";
echo "-------------------------------------------------------------------";

?>


<html>
<head>
<link rel="stylesheet" href="cdshousai.css" type="text/css" />
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<script type="text/javascript" src="http://www.google.com/jsapi"></script>  
<script type="text/javascript">google.load("jquery", "1.2");</script>
<script type="text/javascript" src="cdshousai.js"></script>
</head>
<body>
<div id = "container">
	<div id ="mainbox">
		<div id="page_hanbetu"><p>CD一枚の詳細ページ</p></div>
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
		<h4>ジャンル検索</h4>
		<ul>

				<li id ="#"><a href ="jyannru.html">jpop</a></li>
				<li id ="#"><a href ="jyannru.html">洋楽</a></li>
				<li id ="#"><a href ="jyannru.html">kpop.アジア</a></li>
				<li id ="#"><a href ="jyannru.html">ワールド</a></li>
				<li id ="#"><a href ="jyannru.html">レゲエ</a></li>
				<li id ="#"><a href ="jyannru.html">ロック</a></li>
				<li id ="#"><a href ="jyannru.html">エレクトロニカ</a></li>
				<li id ="#"><a href ="jyannru.html">ダンス.ハウス</a></li>
				<li id ="#"><a href ="jyannru.html">ヒーリング</a></li>
				<li id ="#"><a href ="jyannru.html">クラシック洋</a></li>
				<li id ="#"><a href ="jyannru.html">クラシック邦</a></li>
				<li id ="#"><a href ="jyannru.html">アニメ映画</a></li>
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
	
		<div id="imgs">
			<!--<div id ="cdimg"></div>-->
			
		<img src="./img/yuki3.png" alt = "cd" width = 200 height =200>
		
		</div>

		<div id ="sichou">
			<table>
				<tr>
					<td>
					1
					</td>
					<td>
					曲名*************************
					</td>
				</tr>
				<tr>
					<td>
					2
					</td>
					<td>
					曲名*************************
					</td>
				</tr>
				<tr>
					<td>
					3
					</td>
					<td>
					曲名*************************
					</td>
				</tr>
				<tr>
					<td>
					4
					</td>
					<td>
					曲名*************************
					</td>
				</tr>
				<tr>
					<td>
					5
					</td>
					<td>
					曲名*************************
					</td>
				</tr>
				<tr>
					<td>
					6
					</td>
					<td>
					曲名*************************
					</td>
					<tr>
					</tr>
					<td>
					7
					</td>
					<td>
					曲名*************************
					</td>
				</tr>
				<tr>
					<td>
					8
					</td>
					<td>
					曲名*************************
					</td>
				</tr>
				<tr>
					<td>
					9
					</td>
					<td>
					曲名*************************
					</td>
				</tr>
			</table>
		</div>
	
					
		<div id = "tx_center_c_l">
		
		
		<h2>アーティストプロフィール</h2>
		小学校時代からの同級生である水野良樹と山下穂尊が男性2人組アマチュアバンドを結成し、1999年（平成11年）2月に路上ライブを開始する。同年11月にボーカルの吉岡聖恵が加わり現在の男女3人組となった。

バンド名は結成した際に水野と山下の唯一の共通点であった、小学生時代に金魚に餌をあげる「生き物係」だったことに由来している。当初「いきものがかり」は仮称で吉岡の加入を契機にバンド名の変更が検討されたが[5]、吉岡が「いきものがかり」の名称を気に入っていたためバンド名は変更されずに現在に至っている[6]。










	
	
	    <div id='carousel_container'>  
      <div id='left_scroll'><img src='left.png' /></div>  
      <div id='carousel_inner'>  
            <ul id='carousel_ul'>  
                <li onclick="ReWrite(1)"><a href='#'><img src='./img/1.png' /></a></li>  
                <li onclick="rewrite(2)"><a href='#'><img src='./img/2.png' /></a></li>  
                <li onclick="rewrite(3)"><a href='#'><img src='./img/3.png' /></a></li>  
                <li onclick="rewrite(4)"><a href='#'><img src='./img/4.png' /></a></li>  
                <li onclick="rewrite(5)"><a href='#'><img src='./img/5.png' /></a></li>  
				<li onclick="rewrite(4)"><a href='#'><img src='./img/4.png' /></a></li>  
                <li onclick="rewrite(2)"><a href='#'><img src='./img/2.png' /></a></li>  
                <li onclick="rewrite(3)"><a href='#'><img src='./img/3.png' /></a></li>  
                <li onclick="rewrite(4)"><a href='#'><img src='./img/4.png' /></a></li>  
                <li onclick="rewrite(5)"><a href='#'><img src='./img/5.png' /></a></li> 
                <li onclick="rewrite(4)"><a href='#'><img src='./img/4.png' /></a></li>  
                <li onclick="rewrite(2)"><a href='#'><img src='./img/2.png' /></a></li>  
                <li onclick="rewrite(3)"><a href='#'><img src='./img/3.png' /></a></li>  
                <li onclick="rewrite(4)"><a href='#'><img src='./img/4.png' /></a></li>  
                <li onclick="rewrite(5)"><a href='#'><img src='./img/5.png' /></a></li>   
            </ul>  
      </div>  
      <div id='right_scroll'><img src='right.png' /></div>  
    </div>
	<script type="text/javascript">


function ReWrite(num)
{
  if (document.getElementById)
  {
    if (num == 0)
    {
	  document.getElementById("gyou_itiran").innerHTML="<ul> <li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>aiko</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>aiko</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>aiko</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'></a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>aiko</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>aiko</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>aiko</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>aiko</a></li></ul>";

    }
    else if(num == 1)
    {
      document.getElementById("gyou_itiran").innerHTML="<ul> <li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li></ul>";
    }  
    else if(num == 2)
	{
	document.getElementById("gyou_itiran").innerHTML="<ul> <li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li></ul>";
}
  }
}

</script>	
<!--<script type="text/javascript">


function rewrite(num)
{
  if (document.getElementById)
  {
    if (num == 1)
    {
	  document.getElementById("imgs").innerHTML="<img src="./img/yuki2.png" alt = "cd" width = 200 height =200>";

    }
    else if(num == 1)
    {
      document.getElementById("gyou_itiran").innerHTML="<ul> <li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li></ul>";
    }  
    else if(num == 2)
	{
	document.getElementById("gyou_itiran").innerHTML="<ul> <li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li><li><a href ='cdshousai.html'>EARTH</a></li><li><a href ='cdshousai.html'>飯島直子</a></li></ul>";
}
  }
}


</script>-->  
	<div id ="botm">
<table>

<tr>

<td bgcolor="#FF00FF">リリース年月日</td>
<td bgcolor ="#C0C0C0">*******リリース詳細********</td>

</tr>
<tr>
<td bgcolor="#FF00FF">リリース年月日</td>
<td bgcolor ="#C0C0C0">*******リリース詳細********</td>
</tr>
<tr>
	<td bgcolor="#FF00FF">リリース年月日</td>
<td bgcolor ="#C0C0C0">*******リリース詳細********</td>
</tr>
<tr><td bgcolor="#FF00FF">リリース年月日</td>
<td bgcolor ="#C0C0C0">*******リリース詳細********</td>
</tr>
<tr>

<td bgcolor="#FF00FF">リリース年月日</td>
<td bgcolor ="#C0C0C0">*******リリース詳細********</td>

</tr>
<tr>

<td bgcolor="#FF00FF">リリース年月日</td>
<td bgcolor ="#C0C0C0">*******リリース詳細********</td>

</tr>
<tr>

<td bgcolor="#FF00FF">リリース年月日</td>
<td bgcolor ="#C0C0C0">*******リリース詳細********</td>

</tr>
<tr>

<td bgcolor="#FF00FF">リリース年月日</td>
<td bgcolor ="#C0C0C0">*******リリース詳細********</td>

</tr>
<tr>

<td bgcolor="#FF00FF">リリース年月日</td>
<td bgcolor ="#C0C0C0">*******リリース詳細********</td>

</tr>
<tr>

<td bgcolor="#FF00FF">リリース年月日</td>
<td bgcolor ="#C0C0C0">*******リリース詳細********</td>

</tr>
</table>
	<iframe src="https://www.google.com/calendar/embed?src=hgnfk9ogah7q5bc460r1d7mir4%40group.calendar.google.com&ctz=Asia/Tokyo" style="border: 0" width="200" height="200" frameborder="0" scrolling="no"></iframe>
</div>


	</div>
</div>

	<div id = "tx_right">
		芸能人についてのツイッター

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
</script>

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
