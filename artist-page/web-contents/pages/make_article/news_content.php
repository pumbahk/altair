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
<?
$news = isset($_POST['news']) ? $_POST['news']:null; 				//POSTされてきたニュース
$related_artist=isset($_POST['related_artist'])?$_POST['related_artist']:null;
$another_artist=isset($_POST['another_artist'])?$_POST['another_artist']:null;

if(!$news||!$related_artist){

}
elseif($another_artist){
	$related_artist[]=$another_artist;
}
if($news && $related_artist){
?>




	

	<form method="POST" action ="news_content.php">
		<p>ニュースコンテンツ</p>
		<textarea name="news" rows="10" cols="100" value=<?= $news ?>><?= $news ?></textarea>　	
		<div class ="artist_names">
		<?for($i=0;$i<=count($related_artist);$i++){?>
		<p><?=$related_artist[$i] ?></p>
		<?}?>

		</div>
		<input type="text" class="textarea_name" name="another_artist">
		<?for($i=0;$i<=count($related_artist)-1;$i++){?>
		<input type="hidden" name ="related_artist[]" value=<?=$related_artist[$i]?>>
		<?}?>
		<input type="submit" class="btn primary"value="確認">
	</form>

	<form method="POST" action="insert_news.php">
		<input type="hidden" name="news" value=<?=$news?>>
		<?for($i=0;$i<=count($related_artist)-1;$i++){?>					
		<input type="hidden" name ="related_artist[]" value=<?=$related_artist[$i]?>>
		<?}?>
		<input type="submit" class="btn primary"value="登録">

	</form>
	
	
		<in

<?
}
else{
?>
	
		
	
		<form method="POST" action="news_content.php">
			<p>ニュースコンテンツ</p>
			<textarea name="news" rows = "10" cols="100" ></textarea>
			<p>アーティスト名</p>
			<input type="text" class ="textarea_name" name="related_artist[]" size = "50" >　
			
			<input type="submit"  class="btn primary" value ="確認">	
		</form>
	

<?
}
?>
</div>
</body>
</html>


