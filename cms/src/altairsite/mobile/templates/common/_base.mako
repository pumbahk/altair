<%namespace file="../common/tags_mobile.mako" name="m" />
<html lang="ja">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=Shift_JIS" />
<title>楽天チケット-<%block name="title" /></title>
</head>
<body>
<div align="center" style="text-align:center">
<img src="${request.mobile_static_url('altaircms:static/mobile/logo.jpg')}" /><br />
<div style="background-image:url(${request.mobile_static_url('altaircms:static/mobile/bg_bar.gif')});background-color:#cc0000;" bgcolor="#cc0000"><font color="white">${self.title()}</font></div>
</div>
${self.body()}
<hr />
<%block name="fnavi" />
<%include file="../common/_footer.mako"/>
