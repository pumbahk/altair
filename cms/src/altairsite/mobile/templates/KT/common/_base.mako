<%namespace file="../common/tags_mobile.mako" name="m" />
<html lang="ja">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=Shift_JIS" />
<title>キョードー東北モバイルチケット-<%block name="title" /></title>
</head>
<body>
<div align="center" style="text-align:center">
<img src="${request.static_url('altaircms:static/KT/smartphone/img/logo.png')}"/>
</div>
${self.body()}
<hr />
<%block name="fnavi" />
<%include file="../common/_footer.mako"/>
