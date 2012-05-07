<?php

class DatabaseException extends Exception {

}

class Database {

	public $dbh;
	private static $instance;

	private function __construct() {
	}

	public static function getInstance() {
		if (self::$instance == null) {
			self::$instance = new Database();
			self::$instance->connect();
		}	
		var_dump(self::$instance);
		return self::$instance;
	}

	public function connect() {
		if ($this->dbh != null) return false;
		$this->dbh = new mysqli("127.0.0.1:3306", "artistpage_user", 'artistpage_user_pass');
		$this->dbh->select_db("artistpage");
		$this->dbh->set_charset("UTF8");
		return true;
	}

}

?>
