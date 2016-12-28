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
<h2>会員(Member) 一覧</h2>
<div class="col-xs-12">
<div class="btn-toolbar">
<div class="btn-group" role="group">
<a class="btn" href="${request.route_path('members.new')}"><i class="icon-plus"></i> 新規メンバー</a>
<a class="btn" href="#modal-csv-import" data-toggle="modal">インポート</a>
<a class="btn" href="#modal-csv-export" data-toggle="modal">エクスポート</a>
<a class="btn" href="#modal-delete-import" data-toggle="modal">メンバー一括削除</a>
</div>
<!-- Search Form -->
<fieldset>
<legend>検索条件</legend>
<form action="${request.route_path('members.index')}" method="GET" class="form-inline">
<div class="form-group">
  <%
      search_name = "" if request.params.get('search_name') == None else request.params.get('search_name')
      search_auth_identifier = "" if request.params.get('search_auth_identifier') == None else request.params.get('search_auth_identifier')
      search_tel_1 = "" if request.params.get('search_tel_1') == None else request.params.get('search_tel_1')
  %>
  ${form.search_name(placeholder=form.search_name.label.text, value=search_name)}
  ${form.search_auth_identifier(placeholder=form.search_auth_identifier.label.text, value=search_auth_identifier)}
  ${form.search_tel_1(placeholder=form.search_tel_1.label.text, value=search_tel_1)}
  <button type="submit" class="btn">検索</button>
</div>
</fieldset>
</form>
<!-- /Search Form -->
  % for member_set in member_sets:
    <div class="btn-group" role="group">
    <%
       active_member_set=""
       if request.params.get('member_set_id') and int(request.params.get('member_set_id')) == member_set.id:
           active_member_set = u"active"
    %>
    <a class="btn btn-info ${active_member_set}" href="${request.route_path('members.index') + u'?member_set_id=' + unicode(member_set.id)}">${member_set.name}</a>
    % for member_kind in member_kinds:
      % if member_kind.member_set_id==member_set.id:
        <%
           active_member_kind=""
           if request.params.get('member_kind_id') and int(request.params.get('member_kind_id')) == member_kind.id:
               active_member_kind = u"active"
        %>
        <a class="btn btn-link ${active_member_kind}" href="${request.route_path('members.index') + u'?member_set_id=' + unicode(member_set.id) + u'&member_kind_id=' + unicode(member_kind.id)}">${member_kind.display_name}</a>
      % endif
    % endfor
    </div>
  % endfor
</div>
</div>
<form action="${request.route_path('members.delete')}" method="POST">
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
            (${h.term(membership.valid_since, membership.expire_at, inclusive=False)})
          </li>
        % endfor
        </ul>
      </td>
    </tr>
% endfor
  </tbody>
</table>
<input type="submit" name="doDelete" class="btn btn-danger" value="削除する" data-submit-confirmation-prompt="選択されたメンバーを削除します。よろしいですか?" />
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
<div id="modal-csv-export" class="modal hide" role="dialog" aria-hidden="true">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
    <h3>CSVエクスポート</h3>
  </div>
  <div class="modal-body">
    <ul>
      <li><a href="${request.route_path('members.export', ext='xlsx')}?${request.query_string}">.xlsx形式 (Microsoft Excel 2007以降)</a></li>
      <li><a href="${request.route_path('members.export', ext='xls')}?${request.query_string}">.xls形式 (Microsoft Excel 2007より前)</a></li>
      <li><a href="${request.route_path('members.export', ext='csv')}?${request.query_string}">CSV形式</a></li>
    </ul>
  </div>
  <div class="modal-footer">
    <button class="btn" data-dismiss="modal" aria-hidden="true">閉じる</button>
  </div>
</div>
<form id="modal-delete-import" class="modal hide" role="dialog" aria-hidden="true" action="${request.route_path('members.bulk_delete')}" method="POST" enctype="multipart/form-data">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
    <h3>メンバー一括削除</h3>
  </div>
  <div class="modal-body">
    エクスポート機能で出力された xls / xlsx / csv ファイルと同じ形式のデータを受け取ります。
    <p style="color:red">ログインIDに紐付くすべての会員データが削除されます。<br>この操作は元に戻せません。<br>データを戻すには削除に用いたファイルで再度インポートしてください。</p>
    <input type="file" name="file" />
  </div>
  <div class="modal-footer">
    <button class="btn" data-dismiss="modal" aria-hidden="true">キャンセル</button>
    <button class="btn btn-danger" name="doBulkDelete">削除</button>
  </div>
</form>
