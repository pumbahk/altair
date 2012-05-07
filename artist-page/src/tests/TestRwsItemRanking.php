<?php

require_once 'RwsItemRanking.php';
require_once 'PHPUnit.php';

class TestRwsItemRanking extends PHPUnit_TestCase {
	
	public function TestRwsItemRanking($name) {
		parent::PHPUnit_TestCase($name);
	}

	function testFindByGenreId() {
		$ret = RWS_ItemRanking::find_by_genre_id(200533);
		var_dump($ret);
	}
}

?>
