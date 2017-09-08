<%inherit file="/base.mako" />
<h2>OAuthサーベスプロバイダー一覧</h2>
% for message in request.session.pop_flash():
<div class="alert">
  <button type="button" class="close" data-dismiss="alert">&times;</button>
  <strong>${message}</strong>
</div>
% endfor

% if request.has_permission('manage_service_providers'):
  <a style="margin:10px 0;" class="btn" href="${request.route_path('service_providers.new')}"><i class="icon-plus"></i>新規OAuthサービスプロバイダーを作成する</a>
% endif

<ul class="nav nav-tabs nav-stacked">
  % for sp in service_providers:
  <li><a href="${request.route_path('service_providers.edit', id=sp.id)}">${sp.display_name}</a></li>
  % endfor
</ul>
