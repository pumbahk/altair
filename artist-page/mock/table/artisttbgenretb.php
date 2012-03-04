<?php

$data =array();
$row = 0;
if (($handle = fopen("artist_info.csv", "r")) !== FALSE) {
	  while (($data = fgetcsv($handle, 1000, ","))!== FALSE) {
	  
	  $idar[$row] = $data[0];
	  $namear[$row] = $data[1];
	  $yomigana[$row] =$data[2];
	  $prof[$row] =$data[3];
	  $genre[$row] = $data[4];
	 
	 $row++;
	 }
		
	}

fclose($handle);
	$rw=0;

for($i=0;$i<=$row;$i++){
	echo $idar[$i]."\n";
	echo $namear[$i]."\n";	
	echo $yomigana[$i]."\n";
	echo $prof[$i]."\n";
	echo $genre[$i]."\n";
	echo "\n";
	echo "\n";
	echo "\n";
	$dbh = mysql_connect("127.0.0.1:3306", "root", 'root');
	mysql_selectdb("artistpage");
	mysql_set_charset( "UTF8", $dbh );
	$in_idar = "insert into artist (id) values('".$idar[$i]."')";
	$in_namear = "insert into artist (name) values('".$namear[$i]."')";
	$in_yomiganaar = "insert into artist (yomigana) values('".$yomigana[$i]."')";
	$in_profar = "insert into artist (prof) values('".$prof[$i]."')";
	$in_genre = "insert into genre (name,id) values('".$genre[$i]."','".$i."')";
	$genrexp = explode("/",$genre[$i]);
	$genrexpp = explode(",",$genrexp);
	if(strpos($genrexp,'邦楽')){
		$parent_id = 1;
	}
	else if(strpos($genrexp,'洋楽')){
		$parent_id =2;
	}
	
	$r = count($genrexp);
	$l =count($genrexpp);
	for($o=0;$o<=$r;$o++){
		for($k=0;$k<=$r;$k++){
		echo $genrexpp[$k]."\n";
		$in_genrexpp =  "insert into genrexp (name,id,parent_id) values('".$genrexp[$k]."','".$rw."','".$parent_id."')";
		$rw++;
		mysql_query($in_genrexpp,$dbh);
		}
		 $rw++;
	}

	print_r($genrexpp);
 	 mysql_query($in_idar,$dbh);
 	 mysql_query($in_namear,$dbh);
 	 mysql_query($in_yomiganaar,$dbh);
 	 mysql_query($in_profar,$dbh);
	 mysql_query($in_genre,$dbh);
	
	
	
	
	
}


?>
	
		