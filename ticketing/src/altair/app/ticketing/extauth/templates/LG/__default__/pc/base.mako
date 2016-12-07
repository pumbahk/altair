<!doctype html>
<html>
<head>
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
<header style="margin-top: 50px;">
% if hasattr(_context, 'subtype') and request.authenticated_userid:
LGファンクラブ会員としてログイン (<a href="${request.route_path('extauth.logout', subtype=_context.subtype)}">ログアウトする</a>)
% endif
</header>
<main>
${self.body()}
</main>
<footer>
footer
</footer>
</body>
</html>
