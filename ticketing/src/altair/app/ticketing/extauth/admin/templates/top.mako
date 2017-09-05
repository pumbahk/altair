<%inherit file="/base.mako" />
<style type="text/css">
  .menu-item {
    background-color: #fff;
  }
</style>

<h2>メニュー</h2>
<ul class="nav nav-tabs nav-stacked">
% if request.has_permission('manage_service_providers'):
  <li class="menu-item"><a href="${request.route_path('service_providers.index')}">OAuthServiceProvider</a></li>
% endif
% if request.has_permission('manage_organization'):
  <li class="menu-item"><a href="${request.route_path('organizations.index')}">Organization</a></li>
% endif
% if request.has_permission('manage_operators'):
  <li class="menu-item"><a href="${request.route_path('operators.index')}">Operator</a></li>
% endif
% if request.has_permission('manage_clients'):
  <li class="menu-item"><a href="${request.route_path('oauth_clients.index')}">OAuthClient</a></li>
% endif
% if request.has_permission('manage_member_sets'):
  <li class="menu-item"><a href="${request.route_path('member_sets.index')}">会員種別 (MemberSet)</a></li>
% endif
% if request.has_permission('manage_member_kinds'):
  <li class="menu-item"><a href="${request.route_path('member_kinds.index')}">会員区分 (MemberKind)</a></li>
% endif
% if request.has_permission('manage_members'):
  <li class="menu-item"><a href="${request.route_path('members.index')}">会員 (Member)</a></li>
% endif
</ul>