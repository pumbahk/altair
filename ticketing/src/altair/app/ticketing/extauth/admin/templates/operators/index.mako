<%inherit file="/base.mako" />

% for message in request.session.pop_flash():
<div class="alert">
  <button type="button" class="close" data-dismiss="alert">&times;</button>
  <strong>${message}</strong>
</div>
% endfor
<h2>Operator 一覧</h2>
<a class="btn" href="${request.route_path('operators.new')}"><i class="icon-plus"></i>新規オペレーター</a>
${h.render_bootstrap_pager(operators)}
<form action="${request.route_path('operators.delete')}" method="POST">

<table class="table">
  <thead>
    <tr>
      <th>✔</th>
      <th>組織名</th>
      <th>ログインID</th>
      <th>役割</th>
    </tr>
  </thead>
  <tbody>
% for operator in operators:
    <tr>
      <td><input type="checkbox" name="id" value="${operator.id}"></td>
      <td>${operator.organization.short_name}</td>
      <td><a href="${request.route_path('operators.edit', id=operator.id)}">${operator.auth_identifier}</a></td>
      <td>${operator.role}</td>
    </tr>
% endfor
  </tbody>
</table>
<input type="submit" name="doDelete" class="btn btn-danger" value="削除する" data-submit-confirmation-prompt="選択されたオペレーターを削除します。よろしいですか?" />
</form>
${h.render_bootstrap_pager(operators)}

