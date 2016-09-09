<%inherit file="/base.mako" />
<h2>オーガニゼーション一覧</h2>
% for message in request.session.pop_flash():
<div class="alert">
  <button type="button" class="close" data-dismiss="alert">&times;</button>
  <strong>${message}</strong>
</div>
% endfor

<a href="${request.route_path('organizations.new')}">新規Orgを作成する</a>

<ul>
  % for org in organizations:
  <li><a href="${request.route_path('organizations.edit', id=org.id)}">${org.short_name}</a></li>
  % endfor
</ul>
