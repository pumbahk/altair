<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=1100, user-scalable=yes">
<meta content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no" name="viewport">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="cache-control" content="no-cache">
<meta http-equiv="expires" content="0">
<title>CBCテレビ</title>

<!-- Cascading Style Sheets -->
<link rel="shortcut icon" href="${view_context.static_url('images/favicon.ico')}" />
<link rel="stylesheet" href="${view_context.static_url('css/sanitize.css')}" type="text/css" media="all">
<link rel="stylesheet" href="${view_context.static_url('css/import.css')}" type="text/css" media="all">
<link rel="stylesheet" href="${view_context.static_url('css/custom.css')}" type="text/css" media="all">

</head>
<body>
<%include file="./_header.mako" />
<main class="logout">
${self.body()}
</main>
</body>
</html>
