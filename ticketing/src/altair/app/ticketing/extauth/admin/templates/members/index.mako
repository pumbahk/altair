<%inherit file="/base.mako" />
<style type="text/css">
.table.members tr.disabled > td,
.table.members tr.disabled > td a {
  color: #ccc; 
}
</style>
% for message in request.session.pop_flash():
<div class="alert">
  <button type="button" class="close" data-dismiss="alert">&times;</button>
  <strong>${message}</strong>
</div>
% endfor
<a href="${request.route_path('members.new')}">新規メンバー</a>
<a href="#modal-csv-import" data-toggle="modal">CSVインポート</a>
${h.render_bootstrap_pager(members)}
<form action="${request.route_path('members.delete')}" method="POST">
<input type="submit" name="doDelete" class="btn" value="削除する" />
<table class="table members">
  <thead>
    <tr>
      <th>✔</th>
      <th>ログインID</th>
      <th>氏名</th>
      <th>会員種別</th>
      <th>会員区分</th>
    </tr>
  </thead>
  <tbody>
% for member in members:
    <tr${u' class="disabled"' if not member.enabled else u''|n}>
      <td><input type="checkbox" name="id" value="${member.id}"></td>
      <td><a href="${request.route_path('members.edit', id=member.id)}">${member.auth_identifier}</a></td>
      <td>${member.name}</td>
      <td>${member.member_set.name}</td>
      <td>
        <ul>
        % for membership in member.memberships:
          <li>
            ${membership.member_kind.name}${u': ' + membership.membership_identifier if membership.membership_identifier else u''}
            (${h.term(membership.valid_since, membership.expire_at)})
          </li>
        % endfor
        </ul>
      </td>
    </tr>
% endfor
  </tbody>
</table>
</form>
${h.render_bootstrap_pager(members)}
<form id="modal-csv-import" class="modal hide" role="dialog" aria-hidden="true" action="${request.route_path('members.bulk_add')}" method="POST" enctype="multipart/form-data">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
    <h3>CSVインポート</h3>
  </div>
  <div class="modal-body">
    以下のような形式のxls / xlsx / csvファイルを受け取ります。
<pre>
<b>ログインID,パスワード,会員種別,会員区分,会員ID,開始日,有効期限,削除フラグ</b>
&lt;ログインID(A)&gt;,&lt;パスワード&gt;,&lt会員種別1&gt;,&lt会員区分1&gt;,&lt;会員ID1&gt;,&lt;開始日&gt;,&lt;有効期限&gt;
&lt;ログインID(A)&gt;,&lt;パスワード&gt;,&lt会員種別1&gt;,&lt会員区分2&gt;,&lt;会員ID2&gt;,&lt;開始日&gt;,&lt;有効期限&gt;
&lt;ログインID(B)&gt;,&lt;パスワード&gt;,&lt会員種別1&gt;,&lt会員区分1&gt;,&lt;会員ID3&gt;,&lt;開始日&gt;,&lt;有効期限&gt;
&lt;ログインID(C)&gt;,&lt;パスワード&gt;,&lt会員種別2&gt;,&lt会員区分3&gt;,&lt;会員ID4&gt;,&lt;開始日&gt;,&lt;有効期限&gt;
...
</pre>
    <input type="file" name="file" />
  </div>
  <div class="modal-footer">
    <button class="btn" data-dismiss="modal" aria-hidden="true">キャンセル</button>
    <button class="btn btn-primary" name="doBulkAdd">インポート</button>
  </div>
</form>
