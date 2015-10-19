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
<header>
% if request.authenticated_userid:
楽天会員としてログイン (<a href="${request.route_path('extauth.logout', subtype=_context.subtype)}">ログアウトする</a>)
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
