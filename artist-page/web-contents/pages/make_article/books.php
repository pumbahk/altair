<?php
include 'db.php'

$stmt_artist = $dbh->prepare("select name from artist");
$stmt_artist ->execute();
$stmt_artist ->bind_result($name);
while($stmt_artist -> fetch()){
	$parent_artist_array[] = $names;
}
$stmt_artist ->close();

$artist_array = 
foreach ($namearr as $artist_id => $artist_name) {
	$artist=urlencode($artist_name);
	$xml_str = file_get_contents('http://api.rakuten.co.jp/rws/3.0/rest?developerId=12657057e6e263dfe5dd57b5565078da&operation=BooksCDSearch&version=2011-12-01&artistName='.$artist);
	// 行数をカウント
	$count=0;
	$gyouu = explode(">",$xml_str);
	$forcount = count($gyouu);
	print_r($gyouu);
	echo $artist_name;
	
	echo $forcount."\n";
	for($r=0;$r<=$forcount;$r++){
	// title文字列カウント
		if(stristr($gyouu[$r], 'title')){
			$count++;
		}


	}

	echo "title が含まれている数を数える";
	echo "\n";
	echo $count."\n";
	echo "\n";
	$count = $count/4;
	echo "タイトルの数".$count."\n";
	echo $artist_id."\n";
	$xml_str = str_replace('header:Header', 'Header', $xml_str);
	$xml_str = str_replace('booksCDSearch:BooksCDSearch xmlns:booksCDSearch="http://api.rakuten.co.jp/rws/rest/BooksCDSearch/2011-12-01"', 'booksCDSearch', $xml_str);
	$xml_str = str_replace('booksCDSearch:BooksCDSearch', 'booksCDSearch', $xml_str);

	$xml  = simplexml_load_string($xml_str);


	echo "\n";
	$t =5;
	$tt = 4;
	for ($x=0;$x<=$count;$x++){
		echo $xml->Body->booksCDSearch->Items->Item[$x]->title."\n";
		echo $xml->Body->booksCDSearch->Items->Item[$x]->smallImageUrl."\n";
		$img=$xml->Body->booksCDSearch->Items->Item[$x]->smallImageUrl;
		
		$playList=$xml->Body->booksCDSearch->Items->Item[$x]->playList;
		$salesDate=$xml->Body->booksCDSearch->Items->Item[$x]->salesDate;
		$largeImageUrl=$xml->Body->booksCDSearch->Items->Item[$x]->largeImageUrl;
		
		
		echo "\n";
		$cdname= $xml->Body->booksCDSearch->Items->Item[$x]->title;
		if($cdname != null) {
			$in_cd = "insert into cds (cdname,id,photo,playList,salesDate,largephoto) values('".$cdname."','".$lo."','".$img."','".$playList."','".$salesDate."','".$largeImageUrl."')";
			$in_arcd = "insert into cd_artist (artist_id,cds_id) values('".$artist_id."','".$lo."')";
			mysql_query($in_cd,$dbh);
			mysql_query($in_arcd,$dbh);
			$lo++;
		 }
	}


}	

?>

