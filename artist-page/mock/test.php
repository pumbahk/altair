<?php
$row = 0;
$namearr=array();
$nameexp=array();
if (($handle = fopen("artist.csv", "r")) !== FALSE) {
    while (($data = fgetcsv($handle, 1000, '"')) !== FALSE) {
			if (stristr($data[0], '特集')){			}
			else{
			print_r($data);
			$nameexp = explode("（",$data[0]);
			$namearr[$row] = $nameexp[0];
			echo $data[0], ",", $nameexp[0];
			echo "\n";
			 $num = count($data);
        	$row++;
			}			
	
    }
	}
    fclose($handle);
?>