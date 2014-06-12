<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
  <title>Rakuten Anshin-Checkout Dummy Service</title>
  <style type="text/css">
body {
  padding-top: 60px; /* 60px to make the container go all the way to the bottom of the topbar */
}
</style>
</head>
<body>
  <div class="navbar navbar-fixed-top">
    <div class="navbar-inner">
      <div class="container">
        <a class="brand" href="#">Rakuten Anshin-Checkout Dummy Service</a>
      </div>
    </div>
  </div>
  <div class="container">
    <table class="table">
      <tbody>
        <tr>
          <th>サービス名</th>
          <td>${service_settings['name']}</td>
        </tr>
        <tr>
          <th>サービスID</th>
          <td>${service_settings['service_id']}</td>
        </tr>
        <tr>
          <th>Cart Confirming 機能実行URL</th>
          <td>${service_settings['endpoints']['cart_confirming_url'] or u'(未設定)'}</td>
        </tr>
        <tr>
          <th>注文通知受取URL</th>
          <td>${service_settings['endpoints']['completion_notification_url'] or u'(未設定)'}</td>
        </tr>
        <tr>
          <th>カートID</th>
          <td>${order['order_cart_id']}</td>
        </tr>
        <tr>
          <th>完了ページURL</th>
          <td>${order['order_complete_url']}</td>
        </tr>
        <tr>
          <th>失敗ページURL</th>
          <td>${order['order_failed_url']}</td>
        </tr>
        <tr>
          <th>テストモード</th>
          <td>${order['test_mode']}</td>
        </tr>
      </tbody>
    </table>
    <table class="table">
      <thead>
        <tr>
          <th>ID</td>
          <th>商品名</th>
          <th>価格</th>
          <th>数量</th>
          <th>小計</th>
        </tr>
      </thead>
      <tbody>
      % for item in order['items']:
        <tr>
          <td>${item['id']}</td>
          <td>${item['name']}</td>
          <td>${item['price']}</td>
          <td>${item['quantity']}</td>
          <td>${item['price'] * item['quantity']}</td>
        </tr>
      % endfor
      </tbody>
      <tfoot>
        <tr>
          <td colspan="3">&nbsp;</td>
          <td>総計</th>
          <td>${order['total_amount']}</td>
        </tr>
      </tfoot>
    </table>
    <% flash_messages = request.session.pop_flash() %>
    % if flash_messages:
    <div class="alert alert-block">
      <ul>
    % for message in flash_messages:
        <li>${message}</li>
    % endfor
      </ul>
    </div>
    % endif
    <form method="post">
      <fieldset>
        <legend>決済情報</legend>
        <label class="control-label" for="openid_claimed_id">OpenID Claimed ID</label>
        ${form.openid_claimed_id()}
        ${h.errors_for(form.openid_claimed_id)}
        <label class="control-label" for="used_point">利用ポイント数</label>
        ${form.used_point()}
        ${h.errors_for(form.used_point)}
        <div class="form-actions">
          <input type="submit" name="doAuthorize" class="btn" value="オーソリする" />
          <input type="submit" name="doAuthorizeFailure" class="btn" value="オーソリ失敗にする" />
        </div>
      </fieldset>
    </form>
  </div>
</body>
</html>
<!--
vim: sts=2 sw=2 ts=2 et
-->
