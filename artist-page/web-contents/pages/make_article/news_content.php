<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<link rel="stylesheet" href="css/bootstrap/css/bootstrap.css" type="text/css">

</head>
<body>
<div class="navber navbar-fixed-top">
    <div class="navbar-inner">
      <div class="container">
      <a class="brand">ニュース予約フォーム</a>
	</div>	
   </div>
 </div>
<div id ="main">
<?
$news = isset($_POST['news']) ? $_POST['news']:null;
$related_artist=isset($_POST['related_artist'])?$_POST['related_artist']:null;
$another_artist=isset($_POST['another_artist'])?$_POST['another_artist']:null;

if(!$news||!$related_artist){

	echo "ニュースか関連アーティストが未入力です";
}
elseif($another_artist){
	$related_artist[]=$another_artist;
}
if($news && $related_artist){
?>
<div id ="title"><span class ="label label-important">関連アーティストを増やす</span></div>

<p><?= $news ?></p>

<?for($i=0;$i<=count($related_artist);$i++){?>
<p><?=$related_artist[$i] ?></p>
<?}?>
	

	<form method="POST" action ="news_content.php">
		<input type="hidden" name= "news" value =<?=$news?>>
		<input type="text" name="another_artist">
		<?for($i=0;$i<=count($related_artist)-1;$i++){?>
		<input type="hidden" name ="related_artist[]" value=<?=$related_artist[$i]?>>
		<?}?>
		<input type="submit" class="btn primary"value="この内容で関連アーティストを増やす">
	</form>

	<form method="POST" action="insert_news.php">
		<input type="hidden" name="news" value=<?=$news?>>
		<?for($i=0;$i<=count($related_artist)-1;$i++){?>
		<input type="hidden" name ="related_artist[]" value=<?=$related_artist[$i]?>>
		<?}?>
		<input type="submit" class="btn primary"value="この内容と関連アーティストで登録する">

	</form>
	
	
		<in

<?
}
else{
?>
	
		<div id ="title"><span class ="label label-important">ニュース更新</span></div>	
		
	
		<form method="POST" action="news_content.php">
			<textarea name="news" rows = "4" cols="100" value="ニュース欄" ></textarea>
			
			<input type="text" name="related_artist[]" size = "50" >
			<input type="submit"  class="btn primary" value ="関連アーティストを増やすもしくは登録">	
		</form>
	

<?
}
?>
</div>
</body>
</html>


