
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<link rel="stylesheet" href="css/bootstrap/css/bootstrap.css" type="text/css">
</head>
<body>
<div class="navber navbar-fixed-top">
    <div class="navbar-inner">
      <div class="container">
      <div class="projectname_box"><a class="projectname">アーティストテーブル更新ページ</a></div>
        </div>
   </div>
 </div>
<div id ="main">

<?php

/*if(!$_POST){
        echo "<div class ='error_message'>POSTデータがありません";

?>

        <a href ="/~katosaori/web-contents/pages/make_article/news_content.php">news_content.php</a></div>
<?

exit;}*/



$dbh = new mysqli("127.0.0.1:3306","root",'root');
$dbh -> select_db("artistpage");
$dbh ->set_charset("UTF8");

$new_artist = isset($_POST['new_artist']) ? $_POST['new_artist'] :null;

if($_POST['artist_insert'] != null && $_POST['genre_insert'] !=null && $_POST['yomigana_insert']!=null && $_POST['prof_insert'] != null){
	
		$insert_artist = $_POST['artist_insert'];
		$stmt_count = $dbh->prepare("select count(id) from artist");
		$stmt_count ->execute();
		$stmt_count ->bind_result($count);
		$stmt_count ->fetch();
		$stmt_count ->close();

		$count = 51344;
		
		//新しいアーティストをartistテーブルに入れる
	
			echo "アーティストテーブル　アーティスト名:".$_POST['artist_insert']."<br >";
			echo "アーティストテーブル　アーティストプロフィール:".$_POST['prof_insert']."<br >";
			echo "アーティストテーブル　アーティストよみがな:".$_POST['yomigana_insert']."<br >";
			
			$stmt_insert_artist = $dbh ->prepare("insert into artist values(?,?,?,?)");
			$stmt_insert_artist -> bind_param('isss',$count,$_POST['artist_insert'],$_POST['prof_insert'],$_POST['yomigana_inesrt']);
			$stmt_insert_artist ->execute();
			$stmt_insert_artist ->close();
		
		
		//新しいアーティストのジャンルをgenreテーブルとartist_genreテーブルに入れる
		$stmt_get_genre = $dbh -> prepare("select * from genre");
		$stmt_get_genre ->execute();
		$stmt_get_genre ->bind_result($id,$genre,$parent_id);

		while($stmt_get_genre->fetch()){
		        $genre_[$id]['gen'] = $genre;
		        $genre_[$id]['par']= $parent_id;

		}


		$count_genre = count($genre_)+1;
		$stmt_get_genre ->close();
		$genre_insert= $_POST['genre_insert'];
		$explode_ = explode("/",$genre_insert);
		$count_explode = count($explode_);
		$count_explode = $count_explode;
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

	
		for($i=$count_explode-1;$i>=1;$i--){
		        if($genres[$i]['found'] == 'new'){
			echo "ジャンルテーブル　ID:".$genres[$i]['id']."<br >";
			echo "ジャンルテーブル ジャンル:".$genres[$i]['genre']."<br >";
			echo "ジャンルテーブル パレントID:".$genres[$i]['parent_id']."<br >";
		                $genres[$i]['parent_id']=$genres[$i-1]['id'];
		                $stmt_insert_genre = $dbh->prepare("insert into genre values(?,?,?)");
		                $stmt_insert_genre -> bind_param('isi',$genres[$i]['id'],$genres[$i]['genre'],$genres[$i]['parent_id']);
		                $stmt_insert_genre ->execute();
		                $stmt_insert_genre ->close();

			}
		}

		foreach($genres as  $a => $t){

		echo "アーティストジャンルテーブル　アーティストID:".$count."<br >";
		echo "アーティストジャンルテーブル　ジャンルID:".$t['id']."<br >";
		$count = 700000;
		$stmt_insert_artist_genre = $dbh->prepare("insert into artist_genre values(?,?)");
	        $stmt_insert_artist_genre -> bind_param('ii',$count,$t['id']);
	        $stmt_insert_artist_genre ->execute();
        	$stmt_insert_artist_genre ->close();
		}	

	echo "アーティストページに新規アーティストを追加しました。　<a href = 'news_content.php'>ニュース更新ページに戻る</a><a href='artist_insert.php'>さらにアーティストを新規登録する</a>";

}




/* elseif($new_artist){

	
	?>
		<form method="POST" action="artist_insert.php">
		<table>	
	<?
		for($i=0;$i<=count($new_artist)-1;$i++){
			?>
			<tr><td>
			<?
			echo $new_artist[$i];
			?>
			</td><td>
			<input type="text" class="textarea_name" name="artist_insert">
			</td><td>
			<input type="text" class="textarea_genre" name="genre_insert">
			</td><td>
			<input type="text" class="textarea_yomigana" name="yomigana_insert">
			</td><td>
			<input type="text" class="textarea_genre" name="prof_insert">
			</td></tr>
		</table>
			<input type="submit" value="新規アーティストとして登録する">
		</form>
		<?
		}
	
} */

elseif($_POST['artist_insert'] == null || $_POST['genre_insert'] ==null || $_POST['yomigana_insert']==null || $_POST['prof_insert']==null){

	echo "未記入の欄があります";
        ?>
        <form method="POST" action="artist_insert.php">
        <table>
	<tr><td>
	<p>アーティスト名</p>
	</td><td>
	<p>ジャンル</p>
	</td><td>
	<p>よみがな</p>
	</td><td>
	<p>プロフィール</p>
	</td></tr>

        <tr><td>
        <input type="text" class="textarea_name" name="artist_insert" value=<?=$_POST['artist_insert']?>>
        </td><td>
        <input type="text" class="textarea_genre" name="genre_insert" value=<?=$_POST['genre_insert']?>>
        </td><td>
        <input type="text" class="textarea_yomigana" name="yomigana_insert" value=<?=$_POST['yomigana_insert']?>>
	</td><td>
	<input type="text" class="textarea_genre" name="prof_insert" value=<?= $_POST['prof_insert']?>>
        </td></tr>
        </table>
        <input type="submit" value="新規アーティストとして登録する">
        </form>


<?


}

else{
	?>
	<form method="POST" action="artist_insert.php">
	<table>
	<tr><td>
	<input type="text" class="textarea_name" name="artist_insert">
	</td><td>
	<input type="text" class="textarea_genre" name="genre_insert">
	</td><td>
	<input type="text" class="textarea_yomigana" name="yomigana_insert">
	</td><td>
	<input type="text" class="textarea_genre" name="prof_insert">
	</td></tr>
	</table>
	<input type="submit" value="新規アーティストとして登録する">	
	</form>
	

<?
	
}
?>
