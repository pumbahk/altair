<%inherit file="/base.mako" />
% for message in request.session.pop_flash():
<div class="alert">
  <button type="button" class="close" data-dismiss="alert">&times;</button>
  <strong>${message}</strong>
</div>
% endfor
<a href="${request.route_path('operators.new')}">新規オペレーター</a>
${h.render_bootstrap_pager(operators)}
<form action="${request.route_path('operators.delete')}" method="POST">
<input type="submit" name="doDelete" class="btn" value="削除する" data-submit-confirmation-prompt="選択されたオペレーターを削除します。よろしいですか?" />
<table class="table">
  <thead>
    <tr>
      <th>✔</th>
      <th>ログインID</th>
      <th>役割</th>
    </tr>
  </thead>
  <tbody>
% for operator in operators:
    <tr>
      <td><input type="checkbox" name="id" value="${operator.id}"></td>
      <td><a href="${request.route_path('operators.edit', id=operator.id)}">${operator.auth_identifier}</a></td>
      <td>${operator.role}</td>
    </tr>
% endfor
  </tbody>
</table>
</form>
${h.render_bootstrap_pager(operators)}

