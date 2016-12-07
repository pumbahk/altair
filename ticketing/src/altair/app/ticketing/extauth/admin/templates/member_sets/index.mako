<%inherit file="/base.mako" />
% for message in request.session.pop_flash():
<div class="alert">
  <button type="button" class="close" data-dismiss="alert">&times;</button>
  <strong>${message}</strong>
</div>
% endfor
<h2>会員種別 (MemberSet) 一覧</h2>
<a class="btn" style="margin:10px 0;" href="${request.route_path('member_sets.new')}"><i class="icon-plus"></i> 新規会員種別</a>
${h.render_bootstrap_pager(member_sets)}
<form action="${request.route_path('member_sets.delete')}" method="POST">

<table class="table">
  <thead>
    <tr>
      <th>✔</th>
      <th>名称</th>
      <th>表示名称</th>
      <th>サブタイプ指定</th>
      <th>パスワード利用</th>
    </tr>
  </thead>
  <tbody>
% for member_set in member_sets:
    <tr>
      <td><input type="checkbox" name="id" value="${member_set.id}"></td>
      <td><a href="${request.route_path('member_sets.edit', id=member_set.id)}">${member_set.name}</a></td>
      <td><a href="${request.route_path('member_sets.edit', id=member_set.id)}">${member_set.display_name}</a></td>
      <td>${member_set.applicable_subtype if member_set.applicable_subtype is not None else u'(すべてに適用)'}</td>
      <td>${u'利用する' if member_set.use_password else u'利用しない'}</td>
    </tr>
% endfor
  </tbody>
</table>
<input type="submit" name="doDelete" class="btn btn-danger" value="削除する" data-submit-confirmation-prompt="選択された会員種別を削除します。よろしいですか?" />
</form>
${h.render_bootstrap_pager(member_sets)}

