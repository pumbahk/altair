<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
</head>
<body>
<?php

$array = array();
$array['artist'][]="artist1";
$array['artist'][]="artist2";
$array['artist'][]="artist3";
$array['artist'][]="artist4";
$array['artist'][]="artist5";


echo count($array)."***";

$array[]="firstkey";
$array[]="secondkey";
$array[]="thirdkey";
$array[]="fouthkey";
$array[]="fifthkey";
$array[]="sixthkey";

echo count($array)."***";
$array['id']="idkey";

$id[]=1;
$id[]=2;
$id[]=3;
$id[]=4;
$id[]=5;

echo count($array)."***";

if($id == $array){
	echo "array==array";
}
else{
	echo "array != array";
}


foreach($array['artist'] as $a){
	$i=0;
	foreach($id as $n){
		$array['artist']['id']=$n;
		$i++;
	}

}



foreach($array as $array => $firstkeys){
	echo "一段階目のキーが".$firstkeys."\n";
}


var_dump($array);


?>
</body>
</html>



