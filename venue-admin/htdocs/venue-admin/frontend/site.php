<?php

$conf = dirname(dirname(dirname(dirname(dirname(__FILE__))))).'/deploy/production/conf/altair.ticketing.admin.ini';

$content = file_get_contents($conf);
if(preg_match('/s3\.access_key\s*=\s*(\S+)/', $content, $matches)) {
	define('AWS_KEY', $matches[1]);
}
if(preg_match('/s3\.secret_key\s*=\s*(\S+)/', $content, $matches)) {
	define('AWS_SECRET', $matches[1]);
}
