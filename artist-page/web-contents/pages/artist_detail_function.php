<?php
include 'db.php';
$artist_name = isset($_GET['artist_rank']) ? $_GET['artist_rank'] :null;
if(!($artist_name)){
	$artist_name = isset($_GET['artist']) ? $_GET['artist'] :null;
}
if(!($artist_name)){
	var_dump($_GET);
	header("Status:404");
	exit("artist not found");
}
function parent_get_genre($id_zero){
	global $dbh;
	$stmt_parent = $dbh->prepare("select genre	from genre where parent_id = ?");
	$stmt_parent->bind_param('i', $id_zero);
	$stmt_parent->execute();
	$stmt_parent->bind_result($parent_genres);	 
	$parent_genres_array = array();		  
	while ($stmt_parent->fetch()) {			 
		 $parent_genres_array[] = $parent_genres;	
	}	  
	$stmt_parent->close();		   
	return $parent_genres_array;
}



function artist_detail_function(){
	global $dbh;
	global $artist_name;
	function photo_get_by_name($dbh,$artist_name) {
		$stmt_genre = $dbh->prepare("select cds.photo,cds.salesDate,cds.largephoto,cds.cdname from cd_artist inner join cds on cds.id = cd_artist.cds_id inner join artist on artist.id = cd_artist.artist_id where artist.name = ?");
		$stmt_genre->bind_param('s',$artist_name);
		$stmt_genre->execute();
		$stmt_genre->bind_result($photo,$salesDate,$largeImage,$cdname);
		while ($stmt_genre->fetch()) {
			$photos[] = compact('photo','salesDate','largeImage','cdname');
		}
		$stmt_genre->close();
		return $photos;
	}

	$photo = photo_get_by_name($dbh,$artist_name);
	$count_photos = count($photo);
	$artist = urlencode($artist_name);
	$xml_str = file_get_contents('http://api.rakuten.co.jp/rws/3.0/rest?developerId=12657057e6e263dfe5dd57b5565078da&operation=BooksCDSearch&version=2011-12-01&artistName='.$artist);
	$count=0;
	$gyouu = explode(">",$xml_str);
	$forcount = count($gyouu);
	for($r=0;$r<=$forcount;$r++){
		// title文字列カウント
		if(isset($gyouu[$r])){
		    if(stristr($gyouu[$r], 'title')){
			    $count++;
			}
		}
	}


	function plof_get_by_name($dbh,$artist_name) {
		$stmt_profs = $dbh->prepare("select prof from artist  where name = ?");
		$stmt_profs->bind_param('s',$artist_name);
		$stmt_profs->execute();
		$stmt_profs->bind_result($prof);
		$stmt_profs->fetch();
		$plofs = $prof; 
		$stmt_profs->close(); 
		return $plofs;
	}
	$plofs = plof_get_by_name($dbh,$artist_name);
		
	return array(
		'photo' => photo_get_by_name($dbh,$artist_name),
		'artist_name' => $artist_name,
		'dbh'=>$dbh,
		'plofs' =>$plofs,
		'p' =>parent_get_genre(0),
		'count' =>$count,	
		'count_photots' =>$count_photos
	);

}
		
