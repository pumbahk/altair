<?php
$row = 0;
$namearr=array();
$count = 0;

//アーティスト名をCSVからとる
if (($handle = fopen("artist_info.csv", "r")) !== FALSE) {
	  while (($data = fgetcsv($handle, 1000, ','))!== FALSE) {
			    echo $data[1]."\n";
			    $namearr[$row]= $data[1];
			 	//artistテーブルにnameを入れる
			 	$dbh = mysql_connect("127.0.0.1:3306", "root", 'root');
				mysql_selectdb("artistpage");
				mysql_set_charset( "UTF8", $dbh );
				$in_name = "insert into artist (name) values('".$namearr[$row]."')";
			
 	 			mysql_query($in_name,$dbh);
        		$row++;
		}				
	}

fclose($handle);
$lo=0;

for($p=0; $p<=$row; $p++){
	
	$artist=urlencode($namearr[$p]);
	$xml_str = file_get_contents('http://api.rakuten.co.jp/rws/3.0/rest?developerId=12657057e6e263dfe5dd57b5565078da&operation=BooksCDSearch&version=2011-12-01&artistName='.$artist);

	// 行数をカウント
	$count=0;

	$gyouu = explode(">",$xml_str);
	$forcount = count($gyouu);
	print_r($gyouu);
	echo $namearr[$p];
	echo "行数\n";
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
echo $p."\n";
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
	echo "\n";
	$cdname= $xml->Body->booksCDSearch->Items->Item[$x]->title;
	if($cdname != null) {
	$in_cd = "insert into cds (cdname,id,photo) values('".$cdname."','".$lo."','".$img."')";
	$in_arcd = "insert into cd_artist (artist_id,cds_id) values('".$p."','".$lo."')";
	 mysql_query($in_cd,$dbh);
	 mysql_query($in_arcd,$dbh);
	 $lo++;
	  }
	}


}	

?>