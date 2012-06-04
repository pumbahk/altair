<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<link rel="stylesheet" href="css/bootstrap/css/bootstrap.css" type="text/css">
</head>
<body>
<div class="navber navbar-fixed-top">
    <div class="navbar-inner">
      <div class="container">
      <div class="projectname_box"><a class="projectname">ニュース予約フォーム</a></div>
        </div>
   </div>
 </div>
<div id ="main">

<?php

if(!$_POST){
	echo "POSTデータがありません news_content.phpから入ってください";

?>

	<a href ="/~katosaori/web-contents/pages/news_content.php">news_content.php</a>
<?

exit;}



$dbh = new mysqli("127.0.0.1:3306","root",'root');
$dbh -> select_db("artistpage");
$dbh ->set_charset("UTF8");

/*confirmedがあったら確認なしでテーブルに入れて更新終わり*/
$confirmed_flag=0;
foreach($_POST as $g){
	if($g=="confirmed"){
		$confirmed_flag=1;
	}
}
if($confirmed_flag){
	$confirmed_array = $_POST; 
	if($confirmed_array['confirmed']){
		/*artistテーブルからidとnameを入れる*/
		$stmt_artist = $dbh->prepare("select id,name from artist");
		$stmt_artist ->execute();
		$stmt_artist ->bind_result($artist_id,$artist_name);
		$count_artist =0;
		$r = 0;
		while($stmt_artist ->fetch()){
			$artist[$r]['artist_name']=$artist_name;
			$artist[$r]['artist_id']=$artist_id;
        	        $count_artist++;
		}
		$stmt_artist ->close();
		$r=0;
		$z=0;
		foreach($confirmed_array as $c => $f){
			if($c == "news_content"){
				$news=$id_or_name;
			}
			elseif($c=="news_id"){
				$news_id=$id_or_name;
			}
		}
		echo "<div class ='insert_done'>artistテーブルとnews_artistテーブルとnewsテーブルを更新しました</div>";
		foreach($confirmed_array as $name_or_rewrite => $id_or_name){
			if($name_or_rewrite=="confirmed"){
			}
			elseif($name_or_rewrite=="rewrite"){ //$_POST['rewrite']が配列になる
	        		foreach($artist as $a){
	                		if($id_or_name[$z]==$a['artist_name']){
						$name[$z]['artist_name']=$id_or_name[$z];
	                		        $name[$z]['artist_id']=$a['artist_id'];
						$stmt_insert_news_artist = $dbh->prepare("insert into news_artist  values(?,?)");
						$stmt_insert_news_aritst ->bind_param('ii',$name[$z]['artist_id'],$news_id);
						$stmt_insert_news_artist ->execute();  
						$stmt_insert_news_artist ->close();
						$z++;
					}
					else{
						$count_artist=$count_artist+1;
						$name[$z]['artist_name']=$id_or_name[$z];
						$name[$z]['artist_id']=$count_artist;
						$stmt_insert_news_artist = $dbh->prepare("insert into news_artist  values(?,?)");
                                                $stmt_insert_news_artist ->bind_param('ii',$name[$z]['artist_id'],$news_id);
                                                $stmt_insert_news_artist ->execute();
						$stmt_insert_news_artist ->close();
						

						/* $stmt_insert_artist = $dbh->prepare(#insert into artist values(?,?,?,?);
						$stmt_insert_artist -> bind_param('isss', , , , );
						$stmt_insert_artist ->execute();
						$stmt_insert_artist ->close();
						*/
						$z++;


					}
	                	}
	
	       		 }
			elseif($name_or_rewrite=="news_content"){
				$news=$id_or_name;
			}
			elseif($name_or_rewrite=="news_id"){
				$news_id=$id_or_name;
			}
	        	else{
				$name[$z]['artist_name']=$name_or_rewrite[$z];
				$name[$z]['artist_id']= $id_or_name[$z];
				$stmt_insert_news_artist = $dbh->prepare("insert into news_artist values(?,?)");
                                $stmt_insert_news_artist ->bind_param('ii',$name[$z]['artist_id'],$news_id);
                                $stmt_insert_news_artist ->execute();
				$stmt_insert_news_artist ->close();
				$z++;
			}
			
		//news_artistテーブルにartist_idと　news_idを入れる
		//news_idがない
		}
	}
	$bikou ="+++";
	$stmt_insert_news = $dbh->prepare("insert into news values(?,?,?)");
	$stmt_insert_news -> bind_param('sis',$news,$news_id,$bikou);
	$stmt_insert_news ->execute();
	$stmt_insert_news ->close();


	exit;
}
/*新規アーティストがいたら確認するいなかったらそのままnews_artistテーブルに入れる*/

else{
	$newstopic['news'] = isset($_POST['news'])? $_POST['news']:null;
	$newstopic['artists']=isset($_POST['related_artist'])? $_POST['related_artist']:null;
	$newstopic_with_nonull = array();
	for($i=0;$i<=count($newstopic['artists']);$i++){
		if($newstopic['artists'][$i] != null){
			$newstopic_with_nonull[] =$newstopic['artists'][$i];
		}
	}
	$stmt_get_last_newsid = $dbh->prepare("select id from news  order by id DESC limit 1");
	$stmt_get_last_newsid -> execute();
	$stmt_get_last_newsid ->bind_result($news_id);
	$stmt_get_last_newsid ->fetch();
	$stmt_get_last_newsid ->close();
	$news_id = $news_id+1;
	/*artistテーブルからのnameとidを配列に入れる*/
	$stmt_artist = $dbh->prepare("select id,name from artist");
	$stmt_artist ->execute();
	$stmt_artist ->bind_result($artist_id,$artist_name);
	$count_artist =0;
	$artist= array();
	$i=0;
	while($stmt_artist ->fetch()){
		$artist[$i]['artist_name']=$artist_name;
		$artist[$i]['artist_id']=$artist_id;
		$i++;
		$count_artist++;
	}
	$stmt_artist ->close();
	/*ニュースに関連するアーティストがアーティストテーブルに既存のアーティストか調べる　新しかったらnew_artistの配列に入れて表示して再確認させる*/
	$new_artist=array();
	$r=0;
	$i=0;
	$t=0;
	
	foreach($newstopic_with_nonull as $n => $name_){ 
		$flag=1;
		foreach($artist as $a){
			//echo "artist[i]===".$a['artist_name']."*****";
			if($name_==$a['artist_name']){
			//	$name_['id']=$a['artist_id'];
				$with_nonull_id[]=$a['artist_id'];
				$flag=0;
				$no_rewrite[$t]['artist_name']=$a['artist_name'];
				$no_rewrite[$t]['artist_id']=$a['artist_id'];
				$t++;
			}
			$i++;		
		}
		
		if($flag){
			$count_artist++;
			//表示して確かめる、新しいartist.idをふる。
			$new_artist[$r]['artist_name']=$name_;
			$new_artist[$r]['artist_id']=$count_artist;
			$r++;
		}

	}

	/*new_artistを表示して書き換えたらもう一度調べるそれで良かったらもう一度insert_news.phpでartistテーブルに新しく登録する*/
	if($new_artist){
		?>
		<form method="POST" action="artist_insert.php" target="myWindow">
		<?
		foreach($new_artist as $n){?>
			<input type ="hidden" name="new_artist[]" value=<?= $n['artist_name']?>>
		
		<?}
		?>
		<input type ="submit" value="artist_insert.phpでartistテーブルを更新する" onClick="newOpen('artist_insert.php','myWindow',500,500);">

		<form>			
		<!--<p>その名前で新しくartistテーブルに入れる場合でも、もう一度コピペしてフォームを埋めてください。</p>
		<form method="POST" action="insert_news.php">
		<?	
			$r=0;
			foreach($new_artist as $n){
				echo $n['artist_name'];

				$r++;
		?>
				
				 <input type="text" class ="textarea_name" name="rewrite[]" >
			
		<?
			}
			if($no_rewrite){
				foreach($no_rewrite as $n){
	
			?>
					<input type="hidden" name=<?=$n['artist_name']?> value=<?=$n['artist_id']?>>
			<?
				}	
			}
			?>	
				<input type="hidden" name="news_content" value=<?=$newstopic['news'] ?>>
				<input type="hidden" name ="news_id" value=<?= $news_id ?>>
				<input type="hidden" name="confirmed" value="confirmed">
				<input type="submit" class="btn primary" value ="このアーティスト名で良い">
	
				</form>-->
	
<?
			
	}
	elseif(!$new_artist){
		
		$bikou="***";
		?>
		<div class="insert_done">
		<?
		if($newstopic){
			$stmt_insert_news = $dbh->prepare("insert into news values(?,?,?)");
			$stmt_insert_news->bind_param('iss',$news_id,$newstopic['news'],$bikou);
			$stmt_insert_news->execute();
			echo "newsテーブルを更新しました<br />";
			$stmt_insert_news->close();
			$count = count($with_nonull_id);
			for($i=0;$i<=$count-1;$i++){
				$stmt_news_artist = $dbh->prepare("insert into news_artist values(?,?)");
				$stmt_news_artist ->bind_param('ii',$news_id,$with_nonull_id[$i]);
				$stmt_news_artist ->execute;
				echo "news_artistテーブルを更新しました";
				$stmt_news_artist ->close();
			}
			
		}?>
		</div><?
	}
}

?>
</div>
</body>
</html>

