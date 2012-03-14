<?php
$artist=urlencode(青山テルマ);
$xml_str = file_get_contents('http://api.rakuten.co.jp/rws/3.0/rest?developerId=12657057e6e263dfe5dd57b5565078da&operation=BooksCDSearch&version=2011-12-01&artistName='.$artist);

//行数をカウント
$count=0;

$gyouu = explode(">",$xml_str);
$forcount = count($gyouu);
print_r($gyouu);
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
$xml_str = str_replace('header:Header', 'Header', $xml_str);
$xml_str = str_replace('booksCDSearch:BooksCDSearch xmlns:booksCDSearch="http://api.rakuten.co.jp/rws/rest/BooksCDSearch/2011-12-01"', 'booksCDSearch', $xml_str);
$xml_str = str_replace('booksCDSearch:BooksCDSearch', 'booksCDSearch', $xml_str);

$xml  = simplexml_load_string($xml_str);


echo "\n";

for ($x=0;$x<=$count;$x++){
	echo $xml->Body->booksCDSearch->Items->Item[$x]->title;
	echo "\n";
	}
	
?>