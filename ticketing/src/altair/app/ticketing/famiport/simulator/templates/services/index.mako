<%inherit file="/_base.mako" />
<h1>チケットサービス選択画面</h1>
<ul>
  <li>直接発券</li>
  <li><a href="${request.route_path('service.reserved')}">予済発券</a></li>
</ul>
