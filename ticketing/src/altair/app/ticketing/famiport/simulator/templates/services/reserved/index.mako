<%inherit file="/_base.mako" />
<h1>GW選択画面</h1>
<ul>
  % for client in clients:
  <li><a href="${request.route_path('service.reserved.select', _query=dict(client_code=client.code))}">${client.name}</a></li>
  % endfor
</ul>
