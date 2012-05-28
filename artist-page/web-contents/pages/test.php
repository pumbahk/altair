<?php

$post_array=isset($_POST)?$_POST:null;
var_dump($post_array);
?>
<html>
<body>
<form method="POST" action="test.php">
<input type ="text" name="artist1" >
<input type ="text" name="artist2" >
<input type="hidden" name="artist_1" value=1>
<input type="hidden" name="artist_2" value=2>
<input type="submit">
</form>
</body>
</html>



