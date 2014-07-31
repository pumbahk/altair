<?php

$conf = dirname(dirname(dirname(dirname(dirname(__FILE__))))).'/deploy/production/conf/altair.ticketing.admin.ini';

if(preg_match(',//(.+):(.+)@(.+):(\d+)/([^\?]+),', file_get_contents($conf), $matches)) {
	$dbh = new PDO(sprintf('mysql:dbname=%s;host=%s;port=%u', $matches[5], $matches[3], $matches[4]), $matches[1], $matches[2]);
	$dbh->query('set names utf8');
}
