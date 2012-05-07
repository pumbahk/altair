<?php

class RWS_ItemRanking {

	const item_ranking_url = "http://api.rakuten.co.jp/rws/3.0/rest?developerId=12657057e6e263dfe5dd57b5565078da&operation=ItemRanking&version=2010-08-05&genreId=%d";

	public static function find_by_genre_id($genre_id) {

		$url = sprintf(self::item_ranking_url, $genre_id);
		
		$xml_str = file_get_contents($url);
		$xml  = simplexml_load_string($xml_str);
		$items = $xml->Body->children("itemRanking", true)->children();

		$result = array();
		for ($x =0;$x<=9;$x++){
			$item = $items[$x];
			$item_captions = explode("発売日",$item->itemCaption);
			$result[] = array(
				'item_name' 		=> $item->itemName,
				'small_image_url' 	=> $item->smallImageUrl,
				'item_caption' 		=> $item->itemCaption,
				'artist_name' 		=> array_shift($item_captions),
				'artist_caption'	=> join('発売日', $item_captions[1]),
			);
		}	

		return $result;
	
	}

}
