<?php 

$dbh = mysql_connect("127.0.0.1:3306", "root", 'root');
mysql_set_charset( "UTF8", $dbh );
mysql_selectdb("artistpage");

$genre = array(
            'apple'  => 'りんご',
            'orange' => 'みかん',
            'grape'  => 'ぶどう'
          );
for($o=0;$o<=4;$o++){

$ingenre = "insert into genre (name,id) values('".$genre['apple'].",'".$o."')";

}

mysql_query($ingenre,$dbh);
?>