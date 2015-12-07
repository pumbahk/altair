<%inherit file="/base.mako" />
<h2>メニュー</h2>
<ul>
% if request.has_permission('manage_my_organization'):
  <li><a href="${request.route_path('organizations.edit', id=request.operator.organization_id)}">オーガニゼーションの編集</a></li>
% endif
% if request.has_permission('manage_operators'):
  <li><a href="${request.route_path('operators.index')}">オペレーターの編集</a></li>
% endif
% if request.has_permission('manage_oauth_clients'):
  <li><a href="${request.route_path('oauth_clients.index')}">OAuthアカウントの編集</a></li>
% endif
% if request.has_permission('manage_member_sets'):
  <li><a href="${request.route_path('member_sets.index')}">会員種別の編集</a></li>
% endif
% if request.has_permission('manage_member_kinds'):
  <li><a href="${request.route_path('member_kinds.index')}">会員区分の編集</a></li>
% endif
% if request.has_permission('manage_members'):
  <li><a href="${request.route_path('members.index')}">メンバーの編集</a></li>
% endif
</ul>
