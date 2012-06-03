<?php
$dbh = new mysqli("127.0.0.1:3306","root",'root');
$dbh -> select_db("artistpage");
$dbh ->set_charset("UTF8");
$stmt_get_genre = $dbh -> prepare("select * from genre");
$stmt_get_genre ->execute();
$stmt_get_genre ->bind_result($id,$genre,$parent_id);

while($stmt_get_genre->fetch()){
	$genre_[$id]['gen'] = $genre;
	$genre_[$id]['par']= $parent_id;

}


$count_genre = count($genre_)+1;
$stmt_get_genre ->close();
$test_genre = "邦楽/Jポップ/インスト";
$explode_ = explode("/",$test_genre);
$count_explode = count($explode_);
$count_explode = $count_explode+1;
$add=$explode_[0];
for($i=1;$i<=$count_explode-1;$i++){
	$genres[$i-1]['genre'] = $add;
        $flag=0;
        foreach($genre_ as $a => $t){
                if( $genres[$i-1]['genre'] == $t['gen'] ){
                        $genres[$i-1]['id']=$a;
                        $genres[$i-1]['found']="found";
                        $flag=1;
                }
        }
        if($flag==0){
                $genres[$i-1]['id']=$count_genre;
                $genres[$i-1]['found']="new";
                $count_genre++;
        }

	$add .= "/".$explode_[$i];
}

for($i=count_explode-1;$i>=0;$i--){
	if($genres[$i]['found'] == 'new'){
		$genres[$i]['parent_id']=$genres[$i-1]['id'];
		$stmt_insert_genre = $dbh->prepare("insert into genre values(?,?,?)");
		$stmt_insert_genre -> bind_param('isi',$genres[$i]['id'],$genres[$i]['genre'],$genres[$i]['parent_id']);
		$stmt_insert_genre ->execute();
		$stmt_insert_genre ->close();
		
	}
}

var_dump($genres);
$artist_id=600000;
foreach($genres as  $a => $t){
	echo "t".$t;
	echo "a".$a;
	var_dump($t);
	$stmt_insert_genre = $dbh->prepare("insert into artist_genre values(?,?)");
	$stmt_insert_genre -> bind_param('ii',$artist_id,$t['id']);
	$stmt_insert_genre ->execute();
	$stmt_insert_genre ->close();
}

	
	
?>


