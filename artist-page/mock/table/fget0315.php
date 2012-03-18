<?php

$data =array();
$row = 0;
$gnr_ar = array();
$l=0;

$mysqli = new mysqli("127.0.0.1:3306", "root", "root", "artistpage");
mysqli_set_charset($mysqli, "utf8");
/* 接続状況をチェックします */
if (mysqli_connect_errno()) {
    printf("Connect failed: %s\n", mysqli_connect_error());
    exit();
}

$query = "select id,genre from g";

if ($result = $mysqli->query($query)) {

    /* 連想配列を取得します */
	
    while ($row = $result->fetch_assoc()) {
        print $row["name"]."---".$row["id"]."\n";
		$gnr_id = $row["id"];
		$gnr_ar[$row["genre"]] = $gnr_id;
		echo $gnr_ar[$row["genre"]] . "\n"; 
		echo "hello";
		print_r($row);
		echo "end";
		
		$l++;
    }
	

    /* 結果セットを開放します */
    $result->free();
}

/* 接続を閉じます */
$mysqli->close();
				  


				  
$r = 0;	
 $mysqli = new mysqli("127.0.0.1:3306", "root", "root", "artistpage");
					mysqli_set_charset($mysqli, "utf8");
					/* 接続状況をチェックします */
					if (mysqli_connect_errno()) {
					    printf("Connect failed: %s\n", mysqli_connect_error());
					    exit();
					}
			  
if (($handle = fopen("artist_info.csv", "r")) != FALSE) {
	  while (($data = fgetcsv($handle, 1000, ','))!= FALSE) {
		
		 
	 	  
		   
		   $count = 0;
		   if (strlen($data[4]) != 0) {
	 	  	$exp = explode(",",trim($data[4]));
			  $count = count($exp);
		  
		   }
	  
		  print_r($exp);
	 	 	print $count . "\n";
		 
		for($i=0; $i< $count; $i++) {
			  if (!isset($gnr_ar[$exp[$i]])) exit("No genre name >>{$exp[$i]}<<\n");
			  $genre_ID = $gnr_ar[$exp[$i]];
			  $query = "insert into artist_genre (artist_id,genre_id) values(".$r.",".$genre_ID.")";
			  
			  $mysqli->query($query);
			 
        }
		
		 $r++;
	 
	 }
		
 

  /* 接続を閉じます */
$mysqli->close();

fclose($handle);
}

?>
	
		