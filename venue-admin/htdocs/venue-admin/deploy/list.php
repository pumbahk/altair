<?php

require 'db.php';

ini_set('include_path', 'lib:'.ini_get('include_path'));
require 'parser.php';

$parser = new Parser;

$r = $dbh->prepare('SELECT o.name organization, s.id, v.id venue,s.name,v.sub_name,metadata_url,s.created_at FROM Site s INNER JOIN Venue v ON v.site_id=s.id AND v.performance_id is null AND v.deleted_at is null INNER JOIN Organization o ON o.id=v.organization_id WHERE s.deleted_at is null AND NOT (IFNULL(s.backend_metadata_url, s.drawing_url) LIKE "dummy/%") ORDER BY s.name');
$r->execute();
while($t = $r->fetch(PDO::FETCH_ASSOC)) {
	$t['metadata_url_dir'] = preg_replace('{/[^/]+\.json$}', '', $t['metadata_url']);
	$site[] = $t;
}

$data = array(
      'site' => $site,
);
$parser->parse(file_get_contents('template/list.html'), $data);