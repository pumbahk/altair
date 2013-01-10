<?php	
include 'db.php';
function parent_get_genre($id_zero) {
	global $dbh;
	$stmt_parent = $dbh->prepare("select genre  from genre where parent_id = ?");
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


function index_function(){
	global $dbh;
	$rank_set_jap = array();
	$rank_set = array();
	$xml_str = file_get_contents('http://api.rakuten.co.jp/rws/3.0/rest?developerId=12657057e6e263dfe5dd57b5565078da&operation=ItemRanking&version=2010-08-05&genreId=200533');
	$xml_str = str_replace('header:Header','Header',$xml_str);
	$xml_str = str_replace('itemRanking:ItemRanking xmlns:itemRanking="http://api.rakuten.co.jp/rws/rest/ItemRanking/2011-12-01"', 'itemRanking', $xml_str);
	$xml_str = str_replace('itemRanking:ItemRanking', 'itemRanking', $xml_str);
	$xml  = simplexml_load_string($xml_str);
	echo "\n";
	for ($x =0;$x<=9;$x++){
		$rank_set_jap[$x+1] =  $xml->Body->itemRanking->Item[$x]->itemName;
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
	
	
	$img = " <img src='../img/artistpage/rank_icon_new.png'>";
	for($i=0;$i<=9;$i++){
		for($e=0;$e<=9;$e++){
			if($old_rank_array[$i]['itemname'] && $new_rank_array[$e]['itemname']){
			    if($old_rank_array[$i]['itemname']==$new_rank_array[$e]['itemname']){
				    if($old_rank_array[$e]['rank'] == $new_rank_array[$i]['rank']){
					 	$img =' <img src="../img/artistpage/rank_icon_stay.png">';
				    }
				    else if($old_rank_array[$i]['rank'] <= $new_rank_array[$e]['rank']){
					    $img =' <img src="../img/artistpage/rank_icon_down.png">';
				    }
				    else if($old_rank_array[$i]['rank'] >= $new_rank_array[$e]['rank']){
					    $img = '<img src="../img/artistpage/rank_icon_up.png">';
				    }
				}
			}
		}
		 $new_rank_updown_imgs[] =$img; 
	}

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
	$img = "<img src='../img/artistpage/rank_icon_new.gif'>";
	for($i=0;$i<=9;$i++){
		for($e=0;$e<=9;$e++){
			if(isset($new_rank_overseas_array[$e]['itemname'])){
			    if($old_rank_overseas_array[$i]['itemname']==$new_rank_overseas_array[$e]['itemname']){
				    if($old_rank_overseas_array[$e]['rank']==$new_rank_overseas_array[$i]['rank']){
					    $img = '<img src="../img/artistpage/rank_icon_stay.gif">';
				    }
				    else if($old_rank_overseas_array[$i]['rank'] <= $new_rank_overseas_array[$e]['rank']){
					    $img = '<img src="../img/artistpage/rank_icon_down.gif">';
				    }
				    else if($old_rank_overseas_array[$i]['rank'] >= $new_rank_overseas_array[$e]['rank']){
					    $img = '<img src="../img/artistpage/rank_icon_up.gif">';
				    }
				}
	
			}
		}
		 $new_rank_updown_imgs_overseas[] =$img;
	}
	
	return array(
		'p' => parent_get_genre(0),
		'artist_jap' => $artist_jap,
		'imgurl_jap' => $imgurl_jap,
		'new_rank_updown_imgs' => $new_rank_updown_imgs,
		'rank_set_jap' => $rank_set_jap,
		'rank_set' => $rank_set,
		'artist' => $artist,
	);
}


