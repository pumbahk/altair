<%inherit file="../layout.mako" />
<%block name="title">ユーザ管理</%block>
<ul>
  <li><a href="${request.route_path('admin.users.list')}">ユーザ一覧</a></li>
  <li><a href="${request.route_path('admin.users.new')}">ユーザ編集 / 新規登録</a></li>
  <li><a href="${request.route_path('admin.users.show', user_id=1)}">ユーザ詳細</a></li>
</ul>
