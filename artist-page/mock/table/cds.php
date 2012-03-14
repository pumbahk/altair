<?php
$row = 0;
$namearr=array();
$count = 0;

//アーティスト名をCSVからとってくる

if (($handle = fopen("artist.csv", "r")) !== FALSE) {
    while (($data = fgetcsv($handle, 1000, '"')) !== FALSE) {
			if (stristr($data[0], '特集')){			}
			else{
			$nameexp = explode("（",$data[0]);
			$namearr[$row] = $nameexp[0];
			 $num = count($data);
			 //artistテーブルにnameを入れる
			 $dbh = mysql_connect("127.0.0.1:3306", "root", 'root');
			mysql_selectdb("artistpage");
			$in_name = "insert into artist (name) values('".$namearr[$row]."')";
 	 		mysql_query($in_name,$dbh);
        	$row++;
			}				
	}
}
fclose($handle);


for($p=0; $p<=24000; $p++){
	
$artist=urlencode($namearr[$p]);
$xml_str = file_get_contents('http://api.rakuten.co.jp/rws/3.0/rest?developerId=12657057e6e263dfe5dd57b5565078da&operation=BooksCDSearch&version=2011-12-01&artistName='.$artist);

// 行数をカウント
$count=0;

$gyouu = explode(">",$xml_str);
$forcount = count($gyouu);
// print_r($gyouu);
echo $namearr[$p]."\n";
echo "行数\n";
echo $forcount."\n";
for($r=0;$r<=$forcount;$r++){

//title文字列カウント

if(stristr($gyouu[$r], 'title')){
	$count++;
}


}

echo "titleが含まれている数を数える";
echo "\n";
echo $count;
echo "\n";
$count = $count/2;
echo "タイトルの数".$count."\n";
$xml_str = str_replace('header:Header', 'Header', $xml_str);
$xml_str = str_replace('booksCDSearch:BooksCDSearch xmlns:booksCDSearch="http://api.rakuten.co.jp/rws/rest/BooksCDSearch/2011-12-01"', 'booksCDSearch', $xml_str);
$xml_str = str_replace('booksCDSearch:BooksCDSearch', 'booksCDSearch', $xml_str);

$xml  = simplexml_load_string($xml_str);


echo "\n";
$lo = 0;
for ($x=0;$x<=$count;$x++){
	echo $xml->Body->booksCDSearch->Items->Item[$x]->title;
	echo "\n";
	$cdname= $xml->Body->booksCDSearch->Items->Item[$x]->title;
	$in_cd = "insert into cds (cdname,id) values('".$cdname[$x]."','".$lo."')";
 	 mysql_query($in_cd,$dbh);
	  $lo++;
	}


}	

?>