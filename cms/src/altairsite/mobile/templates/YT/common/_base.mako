<%namespace file="../common/tags_mobile.mako" name="m" />
<html lang="ja">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=Shift_JIS" />
<title>ユースシアタージャパン-<%block name="title" /></title>
</head>
<body>
<div align="center" style="text-align:center">
<a href="/">
  <img src="${request.mobile_static_url('altaircms:static/YT/mobile/logo.jpg')}" width="200px"/>
</a>
<br />
<div style="background-color:#892C55;" bgcolor="#892C55"><font color="white">${self.title()}</font></div>
</div>
${self.body()}
<hr />
<%block name="fnavi" />
<%include file="../common/_footer.mako"/>
