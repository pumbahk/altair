<?php

ini_set('include_path', 'lib:'.ini_get('include_path'));

define('APP_ROOT', dirname(dirname(dirname(dirname(__FILE__)))));
define('FRONTEND_STORAGE', APP_ROOT.'/var/venue-layout/frontend');
define('BACKEND_STORAGE', APP_ROOT.'/var/venue-layout/backend');

define('CMD_START_IMPORT_VENUE', APP_ROOT.'/bin/start-import-venue.sh');
define('CMD_IMPORT_VENUE', APP_ROOT.'/bin/import-venue.sh');
define('CMD_REGISTER_FRONTEND', APP_ROOT.'/bin/register-frontend.sh');
define('CMD_LIST_ORGS', APP_ROOT.'/bin/list-organizations');

$conf = dirname(dirname(dirname(dirname(dirname(__FILE__))))).'/deploy/production/conf/altair.ticketing.admin.ini';

$content = file_get_contents($conf);
if(preg_match('/s3\.access_key\s*=\s*(\S+)/', $content, $matches)) {
	define('AWS_KEY', $matches[1]);
}
if(preg_match('/s3\.secret_key\s*=\s*(\S+)/', $content, $matches)) {
	define('AWS_SECRET', $matches[1]);
}
unset($content);