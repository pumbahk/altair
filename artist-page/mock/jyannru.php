<?php
$dbh = new mysqli("127.0.0.1:3306", "root", 'root');
$dbh->select_db("artistpage");
$dbh->set_charset("UTF8");

$genre_name = isset($_GET['genre']) ? $_GET['genre'] : null;

if (!$genre_name) {
	header("Status: 404");
	exit("Genre not found");
} 

function genre_get_by_name($dbh, $genre_name) {
	$stmt_genre = $dbh->prepare("select id, genre, parent_id from g where genre = ?");
	$stmt_genre->bind_param('s', $genre_name);
	$stmt_genre->execute();
	$stmt_genre->bind_result($id, $genre, $parent_id);
	$stmt_genre->fetch();
	$tree = split('/', $genre);
	$stmt_genre->close();
	return compact('id', 'genre', 'parent_id', 'tree');
}

function genre_get_child_by_id($dbh, $genre_id) {
	$stmt_genre_list = $dbh->prepare('select id, genre, parent_id from g where parent_id = ?');
	$stmt_genre_list->bind_param('i', $genre_id);
	$stmt_genre_list->execute();
	$stmt_genre_list->bind_result($id, $genre, $parent_id);
	$retval = array();
	while ($stmt_genre_list->fetch()) {
		$retval[] = compact('id', 'genre', 'parent_id', 'tree'); 
	}
	$stmt_genre_list->close();
	return $retval;
}

$genre = genre_get_by_name($dbh, $genre_name);
$genre_link = "";
foreach ($genre['tree'] as $idx => $tree_genre) {
	$genre_link .= '/' . urlencode($tree_genre);
	if ($idx) print '&gt;';
?>
<a href="/~katosaori/altair-mock/genre<?=$genre_link?>"><?=$tree_genre ?></a>
<?
}

print "<h1>$genre_name</h1>";

$child_genre_list = genre_get_child_by_id($dbh, $genre['id']);
foreach ($child_genre_list as $genre) {
	$genre_tree = split('/', $genre['genre']);
	$genre_link = "";
	foreach ($genre_tree as $g) {
		$genre_link .= '/' . urlencode($g);
	}
?>
	<a href="/~katosaori/altair-mock/genre<?=$genre_link?>"><?= htmlspecialchars($genre['genre'])?></a><br>	
<? echo $genre['id'];?>	
<?
}
	

?>
<?php



echo "----------------------------------------------------------------------";
?>
<html>
<head>
<link rel="stylesheet" href="genre.css" type="text/css" />
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<script type="text/javascript" src="http://www.google.com/jsapi"></script>  
<script type="text/javascript">google.load("jquery", "1.2");</script>
<script type="text/javascript" src="genre.js"></script>
</head>
<body>
<?php
print $_GET['tree'];
var_dump($_GET);

?>
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
			<? for($q=0;$q<=11;$q++): ?>
			<form action="genre.php" method="POST">
			<input type="hidden" name="genre" value ="<?= htmlspecialchars($t[$q]); ?>" >
			 <input type="submit"> 
			</form>
			<li id ='#'><a href ='genre.php'><?= htmlspecialchars($t[$q]); ?></a></li>
			
			
		<? endfor ?>
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
