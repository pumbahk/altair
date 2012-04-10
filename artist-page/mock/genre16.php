<?php
/*
vim: tabstop=4 extandtab:
*/
$dist_genre = array();
$cd_id = 1;

$genres = file("genre_list.txt");
foreach ($genres as $genre) {
        $genre = trim($genre);
	print "-- $genre\n";
        $match = array();
		$e = array();
		$w = array();
		
		$no_parent = array();

		if (!isset($dist_genre[$genre])) {
		$dist_genre[$genre] = array(
			'id' => $cd_id++
		);
		
		
	
			if (preg_match('#(.+)/(.+)$#', $genre, $match)) {
				$dist_genre[$genre]['parent_id'] = $dist_genre[$match[1]]['id'];
				
				if(!isset($dist_genre[$match[1]])){
					
					$dist_genre[$match[1]] = array(
						'id' => $cd_id++
					);
					$dist_genre[$genre]['parent_id'] = $dist_genre[$match[1]]['id'];
					if(preg_match('#(.+)/(.+)$#',$match[1],$e)){
						$dist_genre[$match[1]]['parent_id'] = $dist_genre[$e[1]]['id'];
						
						if(!isset($dist_genre[$e[1]])){
						
							$dist_genre[$e[1]] = array(
								'id' => $cd_id++
							);
							$dist_genre[$match[1]]['parent_id'] = $dist_genre[$e[1]]['id'];
						
							if(preg_match('#(.+)/(.+)$#',$e[1],$w)){
								$dist_genre[$e[1]]['parent_id'] = $dist_genre[$w[1]]['id'];
								
								if(!isset($dist_genre[$w[1]])){
								
									$dist_genre[$w[1]] = array(
										'id' => $cd_id++
									);
									$dist_genre[$e[1]]['parent_id'] = $dist_genre[$w[1]]['id'];
								}
							}
						
						
				
						}
					}
				}
				
				
				
			}
		}
			
}
		
			
    
		
$dbh = mysql_connect("127.0.0.1:3306", "root", 'root');
mysql_selectdb("artistpage");
mysql_set_charset( "UTF8", $dbh );

foreach ($dist_genre as $k => $d) {
	
	print "{$d['id']},{$k},{$d['parent_id']}\n";
	
	$ig = "insert into g (id,genre,parent_id) values('".$d['id']."','".$k."','".$d['parent_id']."')";
	mysql_query($ig,$dbh);
}
?>