<%inherit file="./footer.mako"/>

<html lang="ja">
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">

</head>
<body bgcolor="#ffffff"><font size="1">
  <div align="center">
      <font color="red">
        
      </font>
	  <a href="${request.route_path("mobile_index")}"><font color="#bf0000" size="3"><img src="/static/mobile/img/logo-small.gif" alt="楽天チケット" width="160" height="26"></font></a>
  <hr size="2" noshade="noshade" color="#bf0000" />

${next.body()}
