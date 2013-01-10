<?php
$dbh = new mysqli("127.0.0.1:3306","artistpage_user",'artistpage_user_pass');
$dbh -> select_db("artistpage");
$dbh -> set_charset("UTF8");
