<?php
	
$dbh = new mysqli("127.0.0.1:3306","artistpage_user",'artistpage_user_pass');
$dbh -> select_db("artistpage");
$dbh -> set_charset("UTF8");

$rank_set_domestic = array();
$rank_set_overseas = array();





/* domestic_ranking_setting_table */

        $xml_str = file_get_contents('http://api.rakuten.co.jp/rws/3.0/rest?developerId=12657057e6e263dfe5dd57b5565078da&operation=ItemRanking&version=2010-08-05&genreId=200533');
        $xml_str = str_replace('header:Header','Header',$xml_str);
        $xml_str = str_replace('itemRanking:ItemRanking xmlns:itemRanking="http://api.rakuten.co.jp/rws/rest/ItemRanking/2011-12-01"', 'itemRanking', $xml_str);
        $xml_str = str_replace('itemRanking:ItemRanking', 'itemRanking', $xml_str);
        $xml  = simplexml_load_string($xml_str);
        echo "\n";
        for ($x =0;$x<=9;$x++){
		
                $rank_set_domestic[$x+1] =  $xml->Body->itemRanking->Item[$x]->itemName;
                $artist_itemcaption_domestic[$x+1] = $xml->Body->itemRanking->Item[$x]->itemCaption;
                $artist_domestic[$x+1] = explode("発売日",$artist_itemcaption_domestic[$x+1]);
		$artist_releasedate_domestic[$x+1]= explode("予約締切日",$artist_domestic[$x+1][1]);
		$rank = $x+1;	
		echo "itemname".$rank_set_domestic[$x+1]."\n";
		echo "rank".$rank."\n";
		echo "artistname".$artist_domestic[$x+1][0]."\n";
		echo "release_date".$artist_releasedate_domestic[$x+1][0]."\n";

		$stmt_parent = $dbh->prepare("INSERT INTO domestic_ranking values(?,?,?,?)");
       		$stmt_parent->bind_param('isss', $rank,$rank_set_domestic[$x+1],$artist_domestic[$x+1][0],$artist_releasedate_domestic[$x+1][0]);
       		$stmt_parent->execute();
       		$stmt_parent->close();

        }



/* overseas_ranking_setting_table */

        $xml_str = file_get_contents('http://api.rakuten.co.jp/rws/3.0/rest?developerId=12657057e6e263dfe5dd57b5565078da&operation=ItemRanking&version=2010-08-05&genreId=200534');
        $xml_str = str_replace('header:Header','Header',$xml_str);
        $xml_str = str_replace('itemRanking:ItemRanking xmlns:itemRanking="http://api.rakuten.co.jp/rws/rest/ItemRanking/2011-12-01"', 'itemRanking', $xml_str);
        $xml_str = str_replace('itemRanking:ItemRanking', 'itemRanking', $xml_str);
        $xml  = simplexml_load_string($xml_str);
        echo "\n";
        for ($x =0;$x<=9;$x++){
                $rank_set_overseas[$x+1] = $xml->Body->itemRanking->Item[$x]->itemName;
                $artist_itemcaption_overseas[$x+1] = $xml->Body->itemRanking->Item[$x]->itemCaption;
                $artist_overseas[$x+1] = explode("発売日",$artist_itemcaption_overseas[$x+1]);
		$artist_releasedate_overseas[$x+1]= explode("予約締切日",$artist_domestic[$x+1][1]);
		$rank = $x+1;

		$stmt_parent = $dbh->prepare("INSERT INTO overseas_ranking values(?,?,?,?)");
       		$stmt_parent->bind_param('isss', $rank, $rank_set_overseas[$x+1],$artist_overseas[$x+1][0],$artist_releasedate_overseas[$x+1][0]);
       		$stmt_parent->execute();
       		$stmt_parent->close();

        }

?>
