<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html lang="ja">
<head>
  <meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
  <title>ファミポートシミュレータ</title>
  <style type="text/css">
body {
  padding-top: 60px; /* 60px to make the container go all the way to the bottom of the topbar */
}

.paid {
  background-color: #ff8;
}

.canceled {
  color: #ddd;
}
</style>
</head>
<body>
  <div class="navbar navbar-fixed-top">
    <div class="navbar-inner">
      <div class="container">
        <a class="brand" href="/">ファミポートシミュレータ</a>
        <ul class="nav pull-right">
          % if hasattr(_context, 'store_code') and _context.store_code:
          <li>店舗コード: ${_context.store_code}</li>
          % endif
          % if hasattr(_context, 'client_code') and _context.client_code:
          <li>クライアント: ${_context.client_code}</li>
          % endif
        </ul>
      </div>
    </div>
  </div>
  <div class="container">
    ${next.body()}
  </div>
</body>
</html>
<!--
vim: sts=2 sw=2 ts=2 et
-->
