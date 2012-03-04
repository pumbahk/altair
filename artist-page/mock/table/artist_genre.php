<?php

if (($handle = fopen("artist_info.csv", "r")) !== FALSE) {
	  while (($data = fgetcsv($handle, 1000, ","))!== FALSE) {

	  $genre[$row] = $data[4];
	 
	 $row++;
	 }
	 }

$dbh = mysql_connect("127.0.0.1:3306", "root", 'root');
mysql_selectdb("artistpage");
mysql_set_charset( "UTF8", $dbh );
$gnr ="select name from gnr2";
$gnrar=mysql_query($gnr,$dbh);
for($f =0; $f<=176; $f++){

$gnrarr = mysql_fetch_assoc($gnrar);


}
	
for($i = 0; $i<=22753; $i++){
	$artist_id = $i;
	
	$slash = explode("/",$genre[$i]);
	$k = count($slash);
	for($m = 0; $m<=$k; $m++){
		for($n =0;$n<=176; $n++){
			if($slash[$m] == $gnrarr[$n]){
				$genre_id = $n;
				$ingenre_artist ="insert into artist_genre (artist_id,genre_id) values('".$i."','".$n."')";
				mysql_query($ingenre_artist,$dbh);
			}
		}
	}
}
	
	
	
?>
