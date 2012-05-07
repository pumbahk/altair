<?php

require_once 'TestRwsItemRanking.php';
require_once 'PHPUnit.php';

$suite = new PHPUnit_TestSuite("TestRwsItemRanking");
$result = PHPUnit::run($suite);

echo $result->toString();
?>
