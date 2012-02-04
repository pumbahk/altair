<form>
  <div class="ui-toolbar">
    <a href="${request.route_path('admin.operator_roles.new')}" class="ui-button">新規ロール</a>
    <a href="${request.route_path('admin.operator_roles.edit_multiple')}" class="ui-button">まとめて編集</a>
    <a href="#" class="ui-button">まとめて削除</a>
  </div>
  <table class="table fullwidth checkboxed_table">
    <thead>
      <tr>
        <th class="minwidth"><input type="checkbox" class="__action__-select_all" /></td>
        <th class="minwidth">ID</th>
        <th>ロール名</th>
        <th>パーミッション</th>
      </tr>
    </thead>
    <tbody>
    % for role in roles.items:
      <tr>
        <td><input type="checkbox" /></td>
        <td><a href="${request.route_path('admin.operator_roles.show', operator_role_id=1)}">${role.id}</a></td>
        <td><a href="${request.route_path('admin.operator_roles.show', operator_role_id=1)}">${role.name}</a></td>
        <td></td>
      </tr>
    % endfor
    </tbody>
  </table>
</form>
