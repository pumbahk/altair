<%inherit file="/base.mako" />
% for message in request.session.pop_flash():
<div class="alert">
  <button type="button" class="close" data-dismiss="alert">&times;</button>
  <strong>${message}</strong>
</div>
% endfor
<h2>会員区分(MemberKind) 一覧</h2>
<a class="btn" href="${request.route_path('member_kinds.new')}" style="margin:10px 0;"><i class="icon-plus"></i>新規会員区分</a>
${h.render_bootstrap_pager(member_kinds)}
<form action="${request.route_path('member_kinds.delete')}" method="POST">

<table class="table">
  <thead>
    <tr>
      <th>✔</th>
      <th>会員種別</th>
      <th>名称</th>
      <th>表示名称</th>
      <th>ランディングページに表示</th>
      <th>ゲストログイン</th>
    </tr>
  </thead>
  <tbody>
% for member_kind in member_kinds:
    <tr>
      <td><input type="checkbox" name="id" value="${member_kind.id}"></td>
      <td>${member_kind.member_set.name}</td>
      <td><a href="${request.route_path('member_kinds.edit', id=member_kind.id)}">${member_kind.name}</a></td>
      <td><a href="${request.route_path('member_kinds.edit', id=member_kind.id)}">${member_kind.display_name}</a></td>
      <td>${u'表示する' if member_kind.show_in_landing_page else u'表示しない'}</td>
      <td>${u'ゲストあり' if member_kind.enable_guests else u'ゲストなし'}</td>
    </tr>
% endfor
  </tbody>
</table>
<input type="submit" name="doDelete" class="btn btn-danger" value="削除する" data-submit-confirmation-prompt="選択された会員区分を削除します。よろしいですか?" />
</form>
${h.render_bootstrap_pager(member_kinds)}

