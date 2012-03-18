<?php

$dbh = mysql_connect("127.0.0.1:3306", "root", 'root');
mysql_selectdb("artistpage");



//イベント情報
 $live_info = "select * from event";
 $live_infoo = mysql_query($live_info,$dbh);
 
 
 echo "<h4>イベント情報</h4>";
  while($row=mysql_fetch_assoc($live_infoo)){
	echo($row['about']);
	echo "			";
	echo($row['genre']);
	echo"			";
	echo($row['date']);
	echo"			";
	echo($row['id']);
	
	echo "<br>";

	}


echo "<br>";






echo "-------------------------------------------------------------------";

?>


<html>
<head>
<link rel="stylesheet" href="live_info.css" type="text/css" />
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<script type="text/javascript" src="http://www.google.com/jsapi"></script>  
<script type="text/javascript">google.load("jquery", "1.2");</script>
<script type="text/javascript" src="genre.js"></script>
<script type="text/javascript" src="jquery.page-scroller-308.js"></script>


</head>
<body>
<div id = "container">
	<div id ="mainbox">
		<div id="page_hanbetu"><p>ライブ情報コンサート情報</p></div>
		<div id ="header">
			<ul>
			<a href="artist_top.html"><li>トップへ</li></a>	<a href="#.html"><li>＊＊＊</li></a>	<a href="#.html"><li>＊＊＊</li></a>	<a href="#.html"><li>＊＊＊</li></a>	
			</ul>

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
			<!--<a href ="artist_top.html">トップへ</a>-->
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
			
			
		</div>
		<div id = "tx_center">
			<div id ="t_u">
<ul>

				<li id ="#"><a href="#pop">pop</a></li>
				<li id ="#"><a href="#enka">演歌</li>
				<li id ="#"><a href="#idol">アイドル</li>
				<li id ="#"><a href="#singer">シンガーソングライター</li>
				<li id ="#"><a href="#showa">昭和歌謡</li>
				<li id ="#"><a href="#ele">エレクトロにか</li>
				<li id ="#"><a href="#indhi">インディーズ</li>
				
		</ul>
	</div>
		
		<div id ="lives_ll">
				<a id="pop"></a>
		<div id ="li_ti"></p>pop</p></div>
				

<div id ="s"><a href ="">植村かな</a>(C)2012 のりつけ雅春・小学館/「アフロ田中」製作委員会

		『アフロ田中』初日舞台挨拶 (東京・埼玉)

		松田翔太が彼女いない歴24年の天然アフロ青年・田中を熱演
	先行抽選 </div>
	<div id ="s"><a href ="">植村かな</a>(C)2012 のりつけ雅春・小学館/「アフロ田中」製作委員会

		『アフロ田中』初日舞台挨拶 (東京・埼玉)

		松田翔太が彼女いない歴24年の天然アフロ青年・田中を熱演
	先行抽選 </div>
	<div id ="s"><a href ="">植村かな</a>(C)2012 のりつけ雅春・小学館/「アフロ田中」製作委員会

		『アフロ田中』初日舞台挨拶 (東京・埼玉)

		松田翔太が彼女いない歴24年の天然アフロ青年・田中を熱演
	先行抽選 </div>
	<div id ="s"><a href ="">植村かな</a>(C)2012 のりつけ雅春・小学館/「アフロ田中」製作委員会

		『アフロ田中』初日舞台挨拶 (東京・埼玉)

		松田翔太が彼女いない歴24年の天然アフロ青年・田中を熱演
	先行抽選 </div>
			</div>

<a id="enka"></a>
			<div id ="lives_ll">
							<div id ="li_ti">演歌</div>

			<div id ="s"><a href ="">植村かな</a>(C)2012 のりつけ雅春・小学館/「アフロ田中」製作委員会

		『アフロ田中』初日舞台挨拶 (東京・埼玉)

		松田翔太が彼女いない歴24年の天然アフロ青年・田中を熱演
	先行抽選 </div>
			</div>
			<a id="idol"></a>

			<div id ="lives_ll">
										<div id ="li_ti">アイドル</div>

				<a href ="">植村かな</a>

		(C)2012 のりつけ雅春・小学館/「アフロ田中」製作委員会

		『アフロ田中』初日舞台挨拶 (東京・埼玉)

		松田翔太が彼女いない歴24年の天然アフロ青年・田中を熱演
		先行抽選 
			</div>
			<div id ="lives_ll">
										<div id ="li_ti">シンガーソングライター</div>
			<a id="singer"></a>

			<a href ="">小泉今日子ライブ</a>

		(C)2012 のりつけ雅春・小学館/「アフロ田中」製作委員会

		『アフロ田中』初日舞台挨拶 (東京・埼玉)

		松田翔太が彼女いない歴24年の天然アフロ青年・田中を熱演
		先行抽選 
		<div id ="s"><a href ="">植村かな</a>(C)2012 のりつけ雅春・小学館/「アフロ田中」製作委員会

		『アフロ田中』初日舞台挨拶 (東京・埼玉)

		松田翔太が彼女いない歴24年の天然アフロ青年・田中を熱演
	先行抽選 </div>
		</div>
<a id="showa"></a>
		<div id ="lives_ll">
							<div id ="li_ti">昭和歌謡</div>

			<a href ="">『アフロ田中』</a>

		(C)2012 のりつけ雅春・小学館/「アフロ田中」製作委員会

		『アフロ田中』初日舞台挨拶 (東京・埼玉)

		松田翔太が彼女いない歴24年の天然アフロ青年・田中を熱演
		先行抽選 
		</div>
<a id="ele"></a>
				<div id ="lives_ll">
										<div id ="li_ti">エレクトロ二カ</div>

			<a href ="">小泉今日子ライブ</a>

		(C)2012 のりつけ雅春・小学館/「アフロ田中」製作委員会

		『アフロ田中』初日舞台挨拶 (東京・埼玉)

		松田翔太が彼女いない歴24年の天然アフロ青年・田中を熱演
		先行抽選 
		</div>
				<div id ="lives_ll">
				<a id="indhi"></a>
		<div id ="li_ti"></p>インディーズ</p></div>
				

<div id ="s"><a href ="">植村かな</a>(C)2012 のりつけ雅春・小学館/「アフロ田中」製作委員会

		『アフロ田中』初日舞台挨拶 (東京・埼玉)

		松田翔太が彼女いない歴24年の天然アフロ青年・田中を熱演
	先行抽選 </div>
	<div id ="s"><a href ="">植村かな</a>(C)2012 のりつけ雅春・小学館/「アフロ田中」製作委員会

		『アフロ田中』初日舞台挨拶 (東京・埼玉)

		松田翔太が彼女いない歴24年の天然アフロ青年・田中を熱演
	先行抽選 </div>
	<div id ="s"><a href ="">植村かな</a>(C)2012 のりつけ雅春・小学館/「アフロ田中」製作委員会

		『アフロ田中』初日舞台挨拶 (東京・埼玉)

		松田翔太が彼女いない歴24年の天然アフロ青年・田中を熱演
	先行抽選 </div>
	<div id ="s"><a href ="">植村かな</a>(C)2012 のりつけ雅春・小学館/「アフロ田中」製作委員会

		『アフロ田中』初日舞台挨拶 (東京・埼玉)

		松田翔太が彼女いない歴24年の天然アフロ青年・田中を熱演
	先行抽選 </div>
			</div>


	</div>
	<div id = "tx_right">
		<!--<script charset="utf-8" src="http://widgets.twimg.com/j/2/widget.js"></script>
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
</div>
</body>
</html>
