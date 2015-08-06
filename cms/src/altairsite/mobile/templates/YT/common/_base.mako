<%namespace file="../common/tags_mobile.mako" name="m" />
<html lang="ja">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=Shift_JIS" />
<title>Youth Theatre Japan（YTJ）公演・イベント チケット情報</title>
<meta name="description" content="Youth Theatre Japan（YTJ）の最新の公演・イベントチケット情報のご案内！Youth Theatre Japan（YTJ）では、ミュージカルやコンサート、ダンスフェスなど多岐に渡る公演・イベントを実施しています。">
<meta name="keywords" content="YTJ,Youth Theatre Japan,公演,チケット,ユースシアタージャパン,劇団,ミュージカル,イベント,コンサート">
</head>
<body>
<div align="center" style="text-align:center">
<a href="/">
  <img src="${request.mobile_static_url('altaircms:static/YT/mobile/logo.jpg')}" width="200px"/>
</a>
<br />
<div style="background-color:#0A1232;" bgcolor="#0A1232"><font color="white">${self.title()}</font></div>
</div>
${self.body()}
<%block name="fnavi" />
<%include file="../common/_footer.mako"/>
