<?php

require_once 'Database.php';

class Genre {

	public static $ROOT_GENRE_ID = 0;
	private $db;

	public function __construct() {
		$this->db = Database::getInstance();	
	}
	public function getGenreByParentId($parentGenreId) {
		$stmt_parent = $this->db->dbh->prepare("select genre from g where parent_id = ?");
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
	
}



?>

