<%def name="band()">
  <div style="background-color:#800000;color:#ffffff" bgcolor="#800000"><font color="#ffffff">${caller.body()}</font></div>
</%def>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html;charset=Shift_JIS">
  <title>Rakuten Anshin-Checkout Dummy Service</title>
</head>
<body>
  <%self:band>Rakuten Anshin-Checkout Dummy Service</%self:band>
  <dl>
    <dt>サービス名</dt>
    <dd>${service_settings['name']}</dd>
    <dt>サービスID</dt>
    <dd>${service_settings['service_id']}</dd>
    <dt>Cart Confirming 機能実行URL</dt>
    <dd>${service_settings['endpoints']['cart_confirming_url'] or u'(未設定)'}</dd>
    <dt>注文通知受取URL</dt>
    <dd>${service_settings['endpoints']['completion_notification_url'] or u'(未設定)'}</dd>
    <dt>カートID</dt>
    <dd>${order['order_cart_id']}</dd>
    <dt>完了ページURL</dt>
    <dd>${order['order_complete_url']}</dd>
    <dt>失敗ページURL</dt>
    <dd>${order['order_failed_url']}</dd>
    <dt>テストモード</dt>
    <dd>${order['test_mode']}</dd>
  </dl>
  <%self:band>購入内容</%self:band>
  <div>
  % for item in order['items']:
    <div>
      [${item['id']}] ${item['name']}<br />
      <div align="right" style="text-align:right">
        ${item['price']}×${item['quantity']}=${item['price'] * item['quantity']}
      </div>
    </div>
  % endfor
    総計<br />
    <div align="right" style="text-align:right">${order['total_amount']}</div>
  </div>
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
<%self:band>決済情報</%self:band>
<form method="post" action="${request.current_route_path()}">
OpenID Claimed ID<br />
${form.openid_claimed_id()}<br />
${h.errors_for(form.openid_claimed_id)}<br />
利用ポイント数<br />
${form.used_points()}<br />
${h.errors_for(form.used_points)}<br />
<input type="submit" name="doAuthorize" class="btn" value="オーソリする (確認画面へ)" />
<input type="submit" name="doAuthorizeFailure" class="btn" value="オーソリ失敗にする" />
</form>
</body>
</html>
<!--
vim: sts=2 sw=2 ts=2 et
-->
