<form>
  <div class="ui-toolbar">
    <a href="${request.route_path('admin.operators.new')}" class="ui-button">新規ユーザ</a>
    <a href="${request.route_path('admin.operators.edit_multiple')}" class="ui-button">まとめて編集</a>
    <a href="${request.route_path('admin.operator_roles.index')}" class="ui-button">ロール設定</a>
    <a href="#" class="ui-button">まとめて削除</a>
  </div>
  <table class="table fullwidth checkboxed_table">
    <thead>
      <tr>
        <th class="minwidth"><input type="checkbox" class="__action__-select_all" /></td>
        <th class="minwidth">ID</th>
        <th>ログインID</th>
        <th>名前</th>
        <th>会社名</th>
        <th>部署名</th>
        <th>ロール</th>
      </tr>
    </thead>
    <tbody>
    % for operator in operators.items:
      <tr>
        <td><input type="checkbox" /></td>
        <td><a href="${request.route_path('admin.operators.show', operator_id=1)}">${operator.id}</a></td>
        <td><a href="${request.route_path('admin.operators.show', operator_id=1)}">${operator.login_id}</a></td>
        <td><a href="${request.route_path('admin.operators.show', operator_id=1)}">${operator.name}</a></td>
        <td><a href="${request.route_path('admin.clients.show', client_id=operator.client.id)}">${operator.client.name}</a></td>
        <td>${operator.client.section_name}</td>
        <td>
            % for role in operator.roles:
            <ul>
                <li><a href="${request.route_path('admin.operator_roles.show', operator_role_id=role.id)}">${role.name}</a></li>
            </ul>
            % endfor
        </td>
      </tr>
    % endfor
    </tbody>
  </table>
</form>
