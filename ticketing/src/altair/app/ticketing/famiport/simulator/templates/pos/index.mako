<%inherit file="/_base.mako" />
<h1>POSメニュー</h1>
<ul>
  <li><a href="${request.route_path('pos.ticketing.entry')}">引換票番号入力</a></li>
  <li><a href="${request.route_path('pos.refund.entry')}">払戻受付</a></li>
</ul>

