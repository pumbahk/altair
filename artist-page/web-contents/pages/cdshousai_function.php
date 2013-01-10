<?php

$genre_name = isset($_GET['genre']) ? $_GET['genre'] : null;
if (!$genre_name) {
	var_dump($_GET);
	header("Status: 404");
	exit("Genre not found");	
} 
$alternate= isset($_GET['alternate']) ? $_GET['alternate'] : null;
$id_zero = 0;
function parent_get_genre($dbh, $id_zero) {
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
//ランキング
$rank_set_jap = array();
$rank_set = array();
$xml_str = file_get_contents('http://api.rakuten.co.jp/rws/3.0/rest?developerId=12657057e6e263dfe5dd57b5565078da&operation=ItemRanking&version=2010-08-05&genreId=200533');
$xml_str = str_replace('header:Header','Header',$xml_str);
$xml_str = str_replace('itemRanking:ItemRanking xmlns:itemRanking="http://api.rakuten.co.jp/rws/rest/ItemRanking/2011-12-01"', 'itemRanking', $xml_str);
$xml_str = str_replace('itemRanking:ItemRanking', 'itemRanking', $xml_str);	   $xml  = simplexml_load_string($xml_str);
echo "\n";
for ($x =0;$x<=9;$x++){			   $rank_set_jap[$x+1] =  $xml->Body->itemRanking->Item[$x]->itemName;
	$imgurl_jap[$x+1] = $xml->Body->itemRanking->Item[$x]->smallImageUrl;
	$artist_long_jap[$x+1] = $xml->Body->itemRanking->Item[$x]->itemCaption;
	$artist_jap[$x+1] = explode("発売日",$artist_long_jap[$x+1]);
}
$xml_str = file_get_contents('http://api.rakuten.co.jp/rws/3.0/rest?developerId=12657057e6e263dfe5dd57b5565078da&operation=ItemRanking&version=2010-08-05&genreId=200534');
$xml_str = str_replace('header:Header','Header',$xml_str);
$xml_str = str_replace('itemRanking:ItemRanking xmlns:itemRanking="http://api.rakuten.co.jp/rws/rest/ItemRanking/2011-12-01"', 'itemRanking', $xml_str);
$xml_str = str_replace('itemRanking:ItemRanking', 'itemRanking', $xml_str);
$xml  = simplexml_load_string($xml_str);
echo "\n";	 
for ($x =0;$x<=9;$x++){
	$rank_set[$x+1] = $xml->Body->itemRanking->Item[$x]->itemName;			 
	$imgurl[$x+1] = $xml->Body->itemRanking->Item[$x]->smallImageUrl;
	$artist_long[$x+1] = $xml->Body->itemRanking->Item[$x]->itemCaption;
	$artist[$x+1] = explode("発売日",$artist_long[$x+1]);
}


//ジャンル
$genre_name = rtrim($genre_name,"/");
	
function genre_get_by_name($dbh, $genre_name) {
	$stmt_genre = $dbh->prepare("select id, genre, parent_id from genre where genre = ?");
	$stmt_genre->bind_param('s', $genre_name);
	$stmt_genre->execute();
	$stmt_genre->bind_result($id, $genre, $parent_id);
	$stmt_genre->fetch();
	$tree = split('/', $genre);
	$stmt_genre->close();
	return compact('id', 'genre', 'parent_id', 'tree');
}

function genre_get_child_by_id($dbh, $genre_id) {
	$stmt_genre_list = $dbh->prepare('select id, genre, parent_id from genre where parent_id = ?');
	$stmt_genre_list->bind_param('i', $genre_id);
	$stmt_genre_list->execute();
	$stmt_genre_list->bind_result($id, $genre, $parent_id);
	$retval = array();
	while ($stmt_genre_list->fetch()) {
		$retval[] = compact('id', 'genre', 'parent_id', 'tree'); 
	}
	$stmt_genre_list->close();
	return $retval;
}

function artist_get_by_genre($dbh,$genre_name) {
	$stmt_genre = $dbh->prepare("select artist.name,artist.yomigana from artist_genre inner join artist on artist_genre.artist_id = artist.id left join genre on artist_genre.genre_id = genre.id where genre.genre = ?" );
	$stmt_genre->bind_param('s',$genre_name);
	$stmt_genre->execute();
	$stmt_genre->bind_result($name,$yomigana);
	while($stmt_genre->fetch()){
		$names[] = compact('name','yomigana');
		}

	$stmt_genre->close();
	return $names;

}
function photo_get_by_genre($dbh,$genre_name) {
	$stmt_genre = $dbh->prepare("select cds.photo from cd_artist inner join cds on cds.id=cd_artist.cds_id inner join artist on artist.id = cd_artist.artist_id  inner join artist_genre on artist_genre.artist_id = artist.id inner join genre on genre.id = artist_genre.genre_id where genre.genre = ?" );
	$stmt_genre->bind_param('s',$genre_name);
	$stmt_genre->execute();
	$stmt_genre->bind_result($photo);
	while($stmt_genre->fetch()){
		$photos[] = compact('photo');
	}

	$stmt_genre->close();
	return $photos;

}

$genre = genre_get_by_name($dbh, $genre_name);
$genre_link = "";
foreach ($genre['tree'] as $idx => $tree_genre) {
	$genre_link .= urlencode($tree_genre).'/';
	

/* ランキングのUPDOWN画像(邦楽) */
$l=0;

$stmt_new_rank = $dbh->prepare("select rank, itemname from domestic_ranking DESK limit 10 offset 10");
$stmt_new_rank->execute();
$stmt_new_rank->bind_result($rank,$itemname);
$new_rank_array = array();
while ($stmt_new_rank->fetch()) {
		$new_rank_array[$l]['rank'] = $rank;
		$new_rank_array[$l]['itemname'] = $itemname;
		$l++;
}
$stmt_new_rank->close();




$l=0;
$stmt_old_rank = $dbh->prepare("select rank, itemname from domestic_ranking DESK limit 10");
$stmt_old_rank->execute();
$stmt_old_rank->bind_result($rank,$itemname);
$old_rank_array = array();
while ($stmt_old_rank->fetch()) {
		$old_rank_array[$l]['rank'] = $rank;
		$old_rank_array[$l]['itemname'] = $itemname;
		$l++;
 }
$stmt_old_rank->close();
echo "\n";


$img = "new";for($i=0;$i<=9;$i++){
		for($e=0;$e<=9;$e++){
				if($old_rank_array[$i][itemname]==$new_rank_array[$e][itemname]){
						if($old_rank_array[$e]['rank'] == $new_rank_array[$i]['rank']){
								$img =' <img src="../img/common/plane.jpg">';
						}						 else if($old_rank_array[$i]['rank'] <= $new_rank_array[$e]['rank']){								 $img =' <img src="../img/common/down.jpg">';
						}
						else if($old_rank_array[$i]['rank'] >= $new_rank_array[$e]['rank']){
								$img = '<img src="../img/common/up.jpg">';
						}

				}
		}
		 $new_rank_updown_imgs[] =$img;
}

/*ランキングのUPDOWN画像(洋楽) */
$l=0;

$stmt_new_rank_overseas = $dbh->prepare("select rank, itemname from overseas_ranking DESK limit 10 offset 10");
$stmt_new_rank_overseas->execute();
$stmt_new_rank_overseas->bind_result($rank,$itemname);
$new_rank_array_overseas = array();
while ($stmt_new_rank_overseas->fetch()) {
		$new_rank_overseas_array[$l]['rank'] = $rank;
		$new_rank_overseas_array[$l]['itemname'] = $itemname;
		$l++;
 }
$stmt_new_rank_overseas->close();
$l=0;
$stmt_old_rank_overseas = $dbh->prepare("select rank, itemname from overseas_ranking DESK limit 10");
$stmt_old_rank_overseas->execute();
$stmt_old_rank_overseas->bind_result($rank,$itemname);
$old_rank_array_overseas = array();
while ($stmt_old_rank_overseas->fetch()) {
		$old_rank_overseas_array[$l]['rank'] = $rank;
		$old_rank_overseas_array[$l]['itemname'] = $itemname;
		$l++;
}
$stmt_old_rank_overseas->close();
echo "\n";
$img = "new";
for($i=0;$i<=9;$i++){
		for($e=0;$e<=9;$e++){
				if($old_rank_overseas_array[$i][itemname]==$new_rank_overseas_array[$e][itemname]){
						if($old_rank_overseas_array[$e]['rank'] == $new_rank_overseas_array[$i]['rank']){
								$img = '<img src="../img/common/plane.jpg">';
						}
						else if($old_rank_overseas_array[$i]['rank'] <= $new_rank_overseas_array[$e]['rank']){
								$img = '<img src="../img/common/down.jpg">';
						}
						else if($old_rank_overseas_array[$i]['rank'] >= $new_rank_overseas_array[$e]['rank']){
								$img = '<img src="../img/common/up.jpg">';
						}

				}
		}
		 $new_rank_updown_imgs_overseas[] =$img;
}
}






	$child_genre_list = genre_get_child_by_id($dbh, $genre['id']);
	$num = 0;
	$links_array = array();
	foreach ($child_genre_list as $genre) {
		$genre_tree = split('/', $genre['genre']);
		$genre_link = "";
		$parent_link = array();
		$z=0;
		foreach ($genre_tree as $g) {
			$genre_link .= urlencode($g).'/';
			$parent_link[$z]=$g;
			$z++;
		}
		$links_array[$num]=htmlspecialchars($genre['genre']);
		$num++;
	}



return array(
	'photo' => $photo,
	'img' =>$img,
	'pattern' => $pattern,
	'cdname' => $cdname,
	'playlist_songs_array' =>$playlist_songs_array,
	'playlist' =>$playlist,
	'count_songs' =>$count_songs,
);


