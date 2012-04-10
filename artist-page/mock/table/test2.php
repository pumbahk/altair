<?php
$samples = array(
    'a/b/c' => array('id' => 1, 'parent_id' => 0),
    'a/b' => array('id' => 2, 'parent_id' => 0),
    'a/b/c/d/e' => array('id' => 3, 'parent_id' => 0),
);

$next_id = 4;

foreach ($samples as $genre => &$record) {
    echo 'genre: ', $genre, "\n";

    $subgenre_list = explode('/', $genre);
    $parent_genre_list = array();
    while (true) {
        $top_genre = array_shift($subgenre_list);
        if (count($subgenre_list) == 0)
            break;
        $parent_genre_list[] = $top_genre;
		print_r($parent_genre_list);
        $parent_genre = implode('/', $parent_genre_list);
        echo 'parent: ', $parent_genre, "\n";
        if (isset($samples[$parent_genre])) {
            echo "  --> ", $samples[$parent_genre]['id'], "\n";
        }
		else if(!isset($samples[$parent_genre])){
			$samples[$parent_genre]['id'] = $next_id;
			echo "  --> ", $samples[$parent_genre]['id'], "\n";
			$next_id++;
		}
			
    }
    echo "--\n";
}
