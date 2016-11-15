<%inherit file="/base.mako" />
<h2>OAuthServiceProviders 一覧</h2>
% for message in request.session.pop_flash():
<div class="alert">
  <button type="button" class="close" data-dismiss="alert">&times;</button>
  <strong>${message}</strong>
</div>
% endfor

<a style="margin:10px 0;" class="btn" href="${request.route_path('service_providers.new')}"><i class="icon-plus"></i>新規OAuthServiceProviderを作成する</a>

<ul class="nav nav-tabs nav-stacked">
  % for sp in service_providers:
  <li><a href="${request.route_path('service_providers.edit', id=sp.id)}">${sp.display_name}</a></li>
  % endfor
</ul>
