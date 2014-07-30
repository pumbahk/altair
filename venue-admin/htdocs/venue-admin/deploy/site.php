<?php

define('APP_ROOT', dirname(dirname(dirname(dirname(__FILE__)))));
define('FRONTEND_STORAGE', APP_ROOT.'/var/venue-layout/frontend');
define('BACKEND_STORAGE', APP_ROOT.'/var/venue-layout/backend');

define('CMD_IMPORT_VENUE', APP_ROOT.'/bin/start-import-venue.sh');
define('CMD_LIST_ORGS', APP_ROOT.'/bin/list-organizations');
