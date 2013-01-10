<?php
$dbh = new mysqli("127.0.0.1:3306","root",'root');
$dbh -> select_db("artistpage");
$dbh -> set_charset("UTF8");

//サイドバーのジャンル一覧
function parent_get_genre($id_zero){
	global $dbh;
	$stmt_parent = $dbh->prepare("select genre from genre where parent_id = ?");
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

function artist_array($a,$b,$genre_id,$page){
	global $dbh;
	$limit = 64;
	$offset = ($page-1) * $limit;
	$page_artist_array = array();
	$stmt_artist_page = $dbh -> prepare("select name,prof from artist where name like ? or artist.name like ? and  name IN ( select name from artist inner join artist_genre on artist.id  = artist_genre.artist_id  where artist_genre.genre_id =?) limit ? offset ?");
	$stmt_artist_page -> bind_param('ssiii',$a,$b,$genre_id,$limit,$offset);
	$stmt_artist_page ->execute();
	$stmt_artist_page ->bind_result($page_artist,$page_artist_prof);
	while($stmt_artist_page ->fetch()){
		$page_artist_array[] = array(
			'name' => $page_artist,
			'prof' => $page_artist_prof,
		);
	}
	return $page_artist_array;
}
function gojyuon_search(){
	global $dbh;
	$figure = isset($_GET['figure']) ? $_GET['figure'] :null;
	$moji = isset($_GET['moji']) ? $_GET['moji'] : null;
	$page = isset($_GET['page']) ? $_GET['page'] :1;
	$page_figure = isset($_GET['page_figure']) ? $_GET['page_figure'] :null;
	$page_moji = isset($_GET['page_moji']) ? $_GET['page_moji'] :null;
	$domestic = isset($_GET['domestic']) ? $_GET['domestic'] :null;
	$overseas = isset($_GET['overseas']) ? $_GET['overseas'] :null;
	$page_overseas = isset($_GET['page_overseas']) ? $_GET['page_overseas'] :null;
	$page_domestic = isset($_GET['page_domestic']) ? $_GET['page_domestic'] :null;
	$count_artist = isset($_GET['count_artist']) ? $_GET['count_artist'] :null;
	if($figure){
		$delimitor = '/,/';
		preg_match($delimitor,$figure,$matches);
		if($matches){
			$figure_explode = explode(",",$figure);
			$figure_explode[0] = $figure_explode[0]."%";
			$figure_explode[1] = $figure_explode[1]."%";
			 //洋楽でカタカナ,ひらがなのアーティストの数
			$stmt_count_artist = $dbh ->prepare("select count(name) from artist inner join artist_genre on artist.id  = artist_genre.artist_id	where artist_genre.genre_id =3 and artist.name like ? or artist.name like ?");
			$stmt_count_artist ->bind_param('ss',$figure_explode[0],$figure_explode[1]);
			$stmt_count_artist ->execute();
			$stmt_count_artist ->bind_result($count_artist);
			$stmt_count_artist->fetch();
			$stmt_count_artist->close();
			$paging = round($count_artist/64);
			$last_page_artist_count = $count_artist%64;
			if($last_page_artist_count){
				 $paging = $paging+1;
			 }
			//1ページめのアーティスト
			$page_artist_array = artist_array($figure_explode[0],$figure_explode[1],3,1);
		}
		else{		
			// 洋楽でアルファベットのアーティストの数
			$figure = $figure."%";
			$stmt_count_artist = $dbh ->prepare("select count(name) from artist inner join artist_genre on artist.id  = artist_genre.artist_id	where artist_genre.genre_id =3 and artist.name like ?");
			$stmt_count_artist ->bind_param('s',$figure);
			$stmt_count_artist ->execute();
			$stmt_count_artist ->bind_result($count_artist);
			$stmt_count_artist->fetch();
			$stmt_count_artist->close();
			$paging=round($count_artist/64);
			$last_page_artist_count = $count_artist%64;
			if($last_page_artist_count){
				$paging = $paging+1;
			}
			//1ページめのアーティスト
			$page_artist_array = artist_array($page_figure."%",$page_figure."%",3,1);
			$page_overseas = 1;
		}
	}
	if($page_figure){
		$delimitor = '/,/';
		preg_match($delimitor,$page_figure,$matches);
		if($matches){
			//洋楽ページ送りのページごとのカタカナ,ひらがなのアーティスト検索
			$page_figure_explode=explode(",",$page_figure);
			$page_figure_explode[0] = $page_figure_explode[0]."%";
			$page_figure_explode[1] = $page_figure_explode[1]."%";
			$paging = round($count_artist/64);
			$last_page_artist_count = $count_artist%64;
			if($last_page_artist_count){
				$paging=$paging+1;
			}
			$page_artist_array = array();
			$page_artist_array = artist_array($page_figure_explode[0],$page_figure_explode[1],3,$page_overseas);
		}
		else{
			//洋楽ページ送りのページごとのアルファベットのアーティスト検索
			$page_artist_array = artist_array($page_figure."%",$page_figure."%",3,$page_overseas);
		}
	}	
	if($moji){
		$delimitor='/,/';
		preg_match($delimitor,$moji,$matches);
		if($matches){
			$moji_explode = explode(",",$moji);
			$moji_explode[0] = $moji_explode[0]."%";
			$moji_explode[1] = $moji_explode[1]."%";
			//邦楽でひらがな,カタカナのアーティストの数
			$stmt_count_artist = $dbh ->prepare("select count(name) from artist inner join artist_genre on artist.id  = artist_genre.artist_id	where artist_genre.genre_id =4 and artist.name like ? or artist.name like ?");
			$stmt_count_artist ->bind_param('ss',$moji_explode[0],$moji_explode[1]);
			$stmt_count_artist ->execute();
			$stmt_count_artist ->bind_result($count_artist);
			$stmt_count_artist->fetch();
			$stmt_count_artist->close();
			$paging = round($count_artist/64);
				$last_page_artist_count = $count_artist%64;
				if($last_page_artist_count){
					$paging = $paging+1;
				}
			//1ページめのアーティスト
				$page_artist_array = artist_array($moji_explode[0],$moji_explode[1],4,1);
				$page_domestic = 1;
			}
			else{
				$moji= $moji."%";
				// 邦楽で英語のアーティストの数
				$stmt_count_artist = $dbh ->prepare("select count(name) from artist inner join artist_genre on artist.id  = artist_genre.artist_id	where artist_genre.genre_id =4 and artist.name like ? or artist.name like ?");
				$stmt_count_artist ->bind_param('ss',$moji,$moji);
				$stmt_count_artist ->execute();
				$stmt_count_artist ->bind_result($count_artist);
				$stmt_count_artist->fetch();
				$stmt_count_artist->close();
				$paging = round($count_artist/64);
				$last_page_artist_count = $count_artist%64;
				if($last_page_artist_count){
					$paging = $paging+1;
				}
				//1ページめのアーティスト
				$page_artist_array = artist_array($moji."%",$moji."%",4,1);
				$page_domestic =1;
			}
		}
		if($page_moji){
				$delimitor = '/,/';
				preg_match($delimitor,$page_moji,$matches);
				if($matches){
					$page_moji_explode=explode(",",$page_moji);
					$page_moji_explode[0] = $page_moji_explode[0]."%";
					$page_moji_explode[1] = $page_moji_explode[1]."%";
					$paging = round($count_artist/64);
					$last_page_artist_count = $count_artist%64;
					if($last_page_artist_count){
						$paging=$paging+1;
					}
				 	$page_artist_array = artist_array($page_moji_explode[0],$page_moji_explode[1],4,$page_domestic);
				}
				else{
					//邦楽　英語ページ送りのページごとのアーティスト検索
					$page_moji = $page_moji."%";
					$paging = round($count_artist/64);
					$last_page_artist_count = $count_artist%64;
					if($last_page_artist_count){
						$paging=$paging+1;
					}
					$page_artist_array = artist_array($page_moji,$page_moji,4,$page_domestic);
				}
		}

		return array(
			'o' => parent_get_genre(0),
			'page_artist_array' => $page_artist_array,
			'paging' => $paging,
			'page_figure' => $page_figure,
			'count_artist' => $count_artist,
			'overseas' => $overseas,
			'figure' => $figure,
			'domestic' => $domestic,
			'moji' => $moji,
			'page_moji' =>$page_moji,
			'page_domestic' =>$page_domestic,
			'page_overseas' => $page_overseas,
		);

}


