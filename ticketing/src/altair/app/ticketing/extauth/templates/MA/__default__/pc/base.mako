<!DOCTYPE html>
<html lang="ja">
<head>
<!--[if lt IE 9]>
<script type="text/javascript" src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
<![endif]-->
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,minimum-scale=1.0,maximum-scale=1.0,user-scalable=no">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="cache-control" content="no-cache">
<meta http-equiv="expires" content="0">
<title>AC長野パルセイロオンラインチケット ログイン</title>

<!-- Cascading Style Sheets -->
<link rel="shortcut icon" href="${view_context.static_url('images/favicon.ico')}" />
<link rel="stylesheet" href="${view_context.static_url('css/main.css')}" type="text/css" media="all">
<link rel="stylesheet" href="${view_context.static_url('css/style.css')}" type="text/css" media="all">
<link rel="stylesheet" href="${view_context.static_url('css/login.css')}" type="text/css" media="all">
<script type="text/javascript" src="${view_context.static_url('js/jquery.js')}"></script>
<script type="text/javascript" src="${view_context.static_url('js/jquery.tile.js')}"></script>
<script type="text/javascript">
$(function(){
    $(window).on('load resize',function(){
        if (787 <= $(this).width()) {
        $(".login-box-2 dl").tile(2);
        }
        else {
            $('.login-box-2 dl').removeAttr('style');
        }
    });
});
</script>
<style type="text/css">
.btn {
  display: inline-block;
  border: 1px solid black;
}

.membership--kind {
  display: block;
}

.membership--membership_id {
  display: block;
}
</style>
</head>
<body>
<%include file="./_header.mako" />
<main>
${self.body()}
</main>
<%include file="./_footer.mako" />
</body>
</html>
