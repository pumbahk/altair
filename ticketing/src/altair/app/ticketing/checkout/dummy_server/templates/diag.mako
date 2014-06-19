<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
  <title>diag</title>
</head>
<body>
  <ul>
  % for payload in payloads:
  <li>
    <p>${payload['name']}</p>
    <form method="post" action="${request.route_path('checkout_dummy_server.stepin')}">
      <input type="hidden" name="checkout" value="${payload['payload']}" />
      <input type="hidden" name="sig" value="${payload['sig']}" />
      <input type="submit" />
    </form>
  </li>
  % endfor
</body>
</html>
<!--
vim: sts=2 sw=2 ts=2 et
-->
