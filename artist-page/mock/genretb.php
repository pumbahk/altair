<?php
$dbh = mysql_connect("127.0.0.1:3306", "root", 'root');
mysql_set_charset( "UTF8", $dbh );
mysql_selectdb("artistpage");
$genre = "select name from genrexp group by name";
$genre_n =mysql_query($genre,$dbh);
//$genre_ar =mysql_fetch_assoc($genre_n);
$row = count($genre_ar);
$genres=array();
for($i=0;$i<=175;$i++){

$genre_ar =mysql_fetch_assoc($genre_n);

//print_r($genre_ar);

$ex=trim("$genre_ar[name]","邦楽洋楽,");
$genres[$i]=$ex;
echo $genres[$i]."\n";

$ingenre = "insert into genre (name,id) values('".$genres[$i]."',".$i.")";

mysql_query($ingenre,$dbh);




}


$gn = "select name from genre group by name";



	
?>