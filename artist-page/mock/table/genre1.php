<?php
$artist=urlencode(青山テルマ);
$xml_str = file_get_contents('http://api.rakuten.co.jp/rws/3.0/rest?developerId=12657057e6e263dfe5dd57b5565078da&operation=GenreSearch&version=2007-04-11&genreId=101311');


$xml_str = str_replace('header:Header', 'Header', $xml_str);
$xml_str = str_replace('genreSearch:GenreSearch xmlns:genreSearch="http://api.rakuten.co.jp/rws/rest/GenreSearch/2011-12-01"', 'booksCDSearch', $xml_str);
$xml_str = str_replace('genreSearch:GenreSearch', 'genreSearch', $xml_str);

$xml  = simplexml_load_string($xml_str);


echo "\n";
$ga = array();
for ($x=0;$x<=20;$x++){
	
	$g = $xml->Body->genreSearch->child[$x]->genreName;
	$gi =$xml->Body->genreSearch->child[$x]->genreId;
	$gaid[$x] = $gi; 
	$ga[$x] = $g;
	echo $g;
	echo "\n";
}
for ($u=0; $u<=20;$u++){
	$xml_str = file_get_contents('http://api.rakuten.co.jp/rws/3.0/rest?developerId=12657057e6e263dfe5dd57b5565078da&operation=GenreSearch&version=2007-04-11&genreId='.$gaid[$u]);
	$xml_str = str_replace('header:Header', 'Header', $xml_str);
	$xml_str = str_replace('genreSearch:GenreSearch xmlns:genreSearch="http://api.rakuten.co.jp/rws/rest/GenreSearch/2011-12-01"', 'booksCDSearch', $xml_str);
	$xml_str = str_replace('genreSearch:GenreSearch', 'genreSearch', $xml_str);

	$xml  = simplexml_load_string($xml_str);
	echo $ga[$u]."\n";
	echo "\n";
	for($w = 0; $w<=20; $w++){
		$t= $xml->Body->genreSearch->child[$w]->genreName;
		$gt[$w] = $t;
		echo $t;
		echo "\n";
	}
}

	
?>