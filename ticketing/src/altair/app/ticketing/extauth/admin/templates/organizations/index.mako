<%inherit file="/base.mako" />
<h2>組織一覧</h2>
% for message in request.session.pop_flash():
<div class="alert">
  <button type="button" class="close" data-dismiss="alert">&times;</button>
  <strong>${message}</strong>
</div>
% endfor

% if request.has_permission('administration'):
    <a style="margin:10px 0;" class="btn" href="${request.route_path('organizations.new')}"><i class="icon-plus"></i>新規Organizationを作成する</a>
% endif

<div class="table-wrap">
    <ul class="nav nav-tabs nav-stacked">
      % for org in organizations:
      <li><a href="${request.route_path('organizations.edit', id=org.id)}">${org.short_name}</a></li>
      % endfor
    </ul>
</div>