<%inherit file="/base.mako" />
  <style type="text/css">
    .menu-wrap {
      margin-bottom: 20px;
    }
    .menu-item {
      background-color: #fff;
    }
</style>

<div class="menu-wrap">
  <h3>組織管理</h3>
  <ul class="nav nav-tabs nav-stacked">
    % if request.has_permission('manage_organization'):
    <li class="menu-item"><a href="${request.route_path('organizations.index')}">組織</a></li>
    % endif
    % if request.has_permission('manage_operators'):
    <li class="menu-item"><a href="${request.route_path('operators.index')}">オペレーター</a></li>
    % endif
    % if request.has_permission('manage_service_providers'):
    <li class="menu-item"><a href="${request.route_path('service_providers.index')}">OAuthサービスプロバイダー</a></li>
    % endif
    % if request.has_permission('manage_clients'):
    <li class="menu-item"><a href="${request.route_path('oauth_clients.index')}">OAuthクライアント</a></li>
    % endif
  </ul>
</div>
<div class="menu-wrap">
  <h3>メンバー管理</h3>
  <ul class="nav nav-tabs nav-stacked">
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
</div>