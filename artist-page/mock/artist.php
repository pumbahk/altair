<?php
$artistname = file_get_contents('./artist.csv');
$itigyou = explode("\n",$artistname);
for($i=0;$i<$itigyou;$i++){
echo $itigyou[i];
}
?>