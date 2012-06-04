<?php

$dbh = new mysqli("127.0.0.1:3306","artistpage_user",'artistpage_user_pass');
$dbh -> select_db("artistpage");
$dbh -> set_charset("UTF8");

$stmt_test=$dbh->prepare("select artist_id,genre_id from artist_genre_cp");
$stmt_test->execute();
$stmt_test->bind_result($artist_ids,$genre_ids);
$r =0;
$genre = '';
while($stmt_test -> fetch()){
	//$genre[$r]= $genre_ids;
	//$artist[$r] = $artist_ids;
//	$bind_artistid_genreid[$r]=compact("genre_ids","artist_ids");
	$bind_artistid_genreid[$artist_ids][] = $genre_ids;
	$r++;
}

//var_dump($bind_artistid_genreid);

$stmt_test -> close();


$count_bind_artistid_genreid = count($bind_artistid_genreid);
$genre_array= array();

$stmt_get_genrename_from_genreid = $dbh ->prepare("select id, parent_id from genre");
$stmt_get_genrename_from_genreid -> execute();
$stmt_get_genrename_from_genreid ->bind_result($id,$parent_id);
$r =0;
while($stmt_get_genrename_from_genreid ->fetch()){
       	$genre_array[$id] = $parent_id;
//       	$genre_array[$r]["id"] = $id;
//		$genre_array[$r]["genre"]=$genre;
		$r++;
}
$stmt_get_genrename_from_genreid -> close();

$bind_artistid_genreid_cp = array();
foreach ($bind_artistid_genreid as $artist_id => $genre_ids) {
    foreach ($genre_ids as $genre_id) {
	    $bind_artistid_genreid_cp[$artist_id][] = $genre_id;
        // 親idを探して追加する
        if (isset($genre_array[$genre_id])) {
    	    $bind_artistid_genreid_cp[$artist_id][] = $genre_array[$genre_id];
        }
        // さらにその親idを探して追加する
        if (isset($genre_array[$genre_array[$genre_id]])) {
    	    $bind_artistid_genreid_cp[$artist_id][] = $genre_array[$genre_array[$genre_id]];
        }
    }
}

foreach($bind_artistid_genreid_cp as $artist_id => $genre_ids){
	foreach($genre_ids as $genre_id){
		echo $artist_id.">>>".$genre_id;
		$stmt_insert_artist_genre = $dbh ->prepare("insert into artist_genre values(?,?)");
		$stmt_insert_artist_genre ->bind_param('ii',$artist_id,$genre_id);
		$stmt_insert_artist_genre ->execute();
		printf("%d File insertada.\n",$stmt->affected_rows);
		$stmt_insert_artist_genre ->close();
	}
}
 
exit;


/*
$i = 0;
foreach ($bind_artistid_genreid as $artist_id => $genre_ids) {
	$artist[$i]["artist"] = $artist_id;
	$artist[$i]["genre"] = $genre_ids;
        $i++;
}
*/
/*
for($i=0;$i<=count($bind_artistid_genreid);$i++){
	for($j=0;$j<=count($genre_array);$j++){
		if($bind_artistid_genreid[$i]["genre_ids"]==$genre_array[$j]["id"]){
			$artist[$i]["artist"] = $bind_artistid_genreid[$i]["artist_ids"];
			$artist[$i]["genre"]=$genre_array[$j]["genre"];
		}
	}
}
*/
for($i=0;$i<=count($artist);$i++){
	$splited_genres = split('/',$artist[$i]["genre"]);
	$add_genres = '';
	for($j=0;$j<=count($splited_genres);$j++){
			if($j==0){
				$add_genres=$splited_genres[$j];
				for($k=0;$k<=count($genre_array);$k++){
					if($add_genres == $genre_array[$k]["genre"]){
						$artist[$i]["genre_ids"][$j]=$genre_array[$k]["id"];
					}
				
				}
			}
			else{
				$add_genres.= "/".$splited_genres[$j];
				for($k=0;$k<=count($genre_array);$k++){
                                        if($splited_genres[0] == $genre_array[$k]["genre"]){
                                                $artist[$i]["genre_ids"][$j]=$genre_array[$k]["id"];
                                        }
                                }
			}
	}
}
var_dump($artist);

exit;







/*
$stmt_get_genrename_from_genreid = $dbh ->prepare("select genre from genre where id = ?");
for($i=0;$i<=$count_bind_artistid_genreid;$i++){
	$id =$bind_artistid_genreid[$i]["genre_ids"];
	$stmt_get_genrename_from_genreid ->bind_param('i',$id);
	$stmt_get_genrename_from_genreid ->execute();
	$stmt_get_genrename_from_genreid ->bind_result($genrename);
	
	while($stmt_get_genrename_from_genreid ->fetch()){	
		$split = split('/',$genrename);
//print $genrename . "\n";
		$r=0;
//var_dump($split);
//print count($split);
		for($j=0;$j<=count($split);$j++){
			$bind_artistid_genreid[$i]["genre_splits"][$r] = $split[$j];
			$r++;
print $r . "\n";
		}
    }
print $i . "\n";
}
$stmt_get_genrename_from_genreid ->close();

print 'success';
exit;

$artist = array();
for($i=0;$i<=$count_bind_artistid_genreid;$i++){
	$count_splits = count($bind_artistid_genreid[$i]["genre_splits"]);

	for($j=0; $j<=$count_splits; $j++){
		if($j=0){
			$add = $bind_artistid_genreid[$i]["genre_splits"][$j];
			$stmt_get_genre_id =$dbh->prepare("select id from genre where genre =?");
			$stmt_get_genre_id ->bind_param('s',$add);
			$stmt_get_genre_id ->execute();
			$stmt_get_genre_id ->bind_result($genre_id);
			$stmt_get_genre_id ->fetch();
			$artist[$i]["splited_id"][$j] = $genre_id;
			echo $artist[$i]["splited_id"][$j];
			$stmt_get_genre_id ->close();
		}
		else{
			$add .= "/".$bind_artistid_genreid[$i]["genre_splits"][$j];
                        $stmt_get_genre_id =$dbh->prepare("select id from genre where genre =?");
                        $stmt_get_genre_id ->bind_param('s',$add);
                        $stmt_get_genre_id ->execute();
                        $stmt_get_genre_id ->bind_result($genre_id);
                        $stmt_get_genre_id ->fetch();
                        $artist[$i]["splited_id"][$j] = $genre_id;
			echo $artist[$i]["splited_id"][$j];
                        $stmt_get_genre_id ->close();
		}
	}
}
*/
?>




