<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<link rel="stylesheet" href="css/bootstrap/css/bootstrap.css" type="text/css">

</head>
<body>
<div class="navber navbar-fixed-top">
    <div class="navbar-inner">
      <div class="container">
        <div class="projectname_box"><a class="projectname">ランキング更新</a></div>
        </div>
   </div>
</div>
<div id ="main">
<?php

$pushed = isset($_POST['pushed']) ? $_POST['pushed']:null;

if($pushed){
	/*$dbh = new mysqli("127.0.0.1:3306","artistpage_user",'artistpage_user_pass');
	$dbh -> select_db("artistpage");
	$dbh -> set_charset("UTF8");
	$rank_set_domestic = array();
	$rank_set_overseas = array();

		$xml_str = file_get_contents('http://api.rakuten.co.jp/rws/3.0/rest?developerId=12657057e6e263dfe5dd57b5565078da&operation=ItemRanking&version=2010-08-05&genreId=200533');
		$xml_str = str_replace('header:Header','Header',$xml_str);
		$xml_str = str_replace('itemRanking:ItemRanking xmlns:itemRanking="http://api.rakuten.co.jp/rws/rest/ItemRanking/2011-12-01"', 'itemRanking', $xml_str);
		$xml_str = str_replace('itemRanking:ItemRanking', 'itemRanking', $xml_str);
		$xml  = simplexml_load_string($xml_str);
		echo "\n";
		for ($x =0;$x<=9;$x++){
			$rank_set_domestic[$x+1] =  $xml->Body->itemRanking->Item[$x]->itemName;
			$artist_itemcaption_domestic[$x+1] = $xml->Body->itemRanking->Item[$x]->itemCaption;
			$artist_domestic[$x+1] = explode("発売日",$artist_itemcaption_domestic[$x+1]);
			$artist_releasedate_domestic[$x+1]= explode("予約締切日",$artist_domestic[$x+1][1]);
			$rank = $x+1;	
			echo "itemname".$rank_set_domestic[$x+1]."\n";
			echo "rank".$rank."\n";
			echo "artistname".$artist_domestic[$x+1][0]."\n";
			echo "release_date".$artist_releasedate_domestic[$x+1][0]."\n";
			$stmt_parent = $dbh->prepare("INSERT INTO domestic_ranking values(?,?,?,?)");
			$stmt_parent->bind_param('isss', $rank,$rank_set_domestic[$x+1],$artist_domestic[$x+1][0],$artist_releasedate_domestic[$x+1][0]);
			$stmt_parent->execute();
			$stmt_parent->close();
		 }
		$xml_str = file_get_contents('http://api.rakuten.co.jp/rws/3.0/rest?developerId=12657057e6e263dfe5dd57b5565078da&operation=ItemRanking&version=2010-08-05&genreId=200534');
		$xml_str = str_replace('header:Header','Header',$xml_str);
		$xml_str = str_replace('itemRanking:ItemRanking xmlns:itemRanking="http://api.rakuten.co.jp/rws/rest/ItemRanking/2011-12-01"', 'itemRanking', $xml_str);
		$xml_str = str_replace('itemRanking:ItemRanking', 'itemRanking', $xml_str);
		$xml  = simplexml_load_string($xml_str);
		echo "\n";
		for ($x =0;$x<=9;$x++){
			$rank_set_overseas[$x+1] = $xml->Body->itemRanking->Item[$x]->itemName;
			$artist_itemcaption_overseas[$x+1] = $xml->Body->itemRanking->Item[$x]->itemCaption;
			$artist_overseas[$x+1] = explode("発売日",$artist_itemcaption_overseas[$x+1]);
			$artist_releasedate_overseas[$x+1]= explode("予約締切日",$artist_domestic[$x+1][1]);
			$rank = $x+1;
			$stmt_parent = $dbh->prepare("INSERT INTO overseas_ranking values(?,?,?,?)");
			$stmt_parent->bind_param('isss', $rank, $rank_set_overseas[$x+1],$artist_overseas[$x+1][0],$artist_releasedate_overseas[$x+1][0]);
			$stmt_parent->execute();
			$stmt_parent->close();
		 }
	*/
	echo "<h3>邦楽ランキングトップ10</h3>";

	foreach($rank_set_domestic as $d){
		echo $d."<br />";
	}
	
	echo "<h3>洋楽ランキングトップ10</h3>";

	foreach($rank_set_overseas as $o){
		echo $o."<br />";
	}
	date_default_timezone_set('Asia/Tokyo');
	$date = date('Y/m/d g:i');
	
	echo $date."日にdomestic_rankingテーブルとoverseas_rankingテーブルを更新しました";

		
	$fp = @fopen("ranking.txt","w") or die("ERROR");
	
	fputs($fp,$date);
	$hougaku = "邦楽ランキングトップ10";
	$yougaku = "洋楽ランキングトップ10";
	fputs($fp,$hougaku);
	foreach($rank_set_domestic as $d){
		$d = $d."<br />";
		fputs($fp,$d);
	}
	fputs($fp,$yougaku);
	foreach($rank_set_overseas as $o){
		$o = $o."<br />";
		fputs($fp,$o);
	}
	
	fclose($fp);
	echo "ファイルranking.txtに日付とランキング更新内容を書き込みました";
	echo "<a href ='ranking.txt'>ranking.txtをみる</a>";

	
}
elseif(!($pushed)){?>
	<form method="POST" action ="ranking_add_record.php" >
	<p>domestic_ranking overseas_rankingテーブルを更新する</p>
	<input type="submit" name = "pushed" class="btn primary" value="更新">
<?}?>



