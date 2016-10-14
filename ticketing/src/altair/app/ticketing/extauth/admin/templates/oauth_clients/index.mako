<%inherit file="/base.mako" />
<style type="text/css">
.client-credential {
  display: inline-block;
}

.click-to-view {
  display: inline-block;
  position: relative;
  border-radius: 1px;
  padding: 0px 0px 0px 1em;
}

.click-to-view::before {
  position: absolute;
  display: inline-block;
  content: "🔑";
  left: 0;
  width: 100%;
  background-color: #fff;
}

.click-to-view::after {
  position: absolute;
  display: inline-block;
  content: "click to see the text";
  color: #888;
  left: 1em;
  padding-left: 2px;
}

.click-to-view:active::before {
  background-color: transparent;
  text-decoration: none;
}

.click-to-view:active::after {
  content: none;
}
</style>
% for message in request.session.pop_flash():
<div class="alert">
  <button type="button" class="close" data-dismiss="alert">&times;</button>
  <strong>${message}</strong>
</div>
% endfor
<h2>OAuthClient 一覧</h2>
<a href="#modal-new-oauth-client" data-toggle="modal" class="btn" style="margin:10px 0;"><i class="icon-plus"></i>新規OAuthClient</a>
<form action="${request.route_path('oauth_clients.delete')}" method="POST">

<table class="table">
  <thead>
    <tr>
      <th>✔</th>
      <th>組織名</th>
      <th>アプリケーション名</th>
      <th>Client ID</th>
      <th>Client Secret</th>
      <th>リダイレクトURI</th>
      <th>スコープ</th>
      <th>有効期限</th>
    </tr>
  </thead>
  <tbody>
% for oauth_client in oauth_clients:
    <tr>
      <td><input type="checkbox" name="id" value="${oauth_client.id}"></td>
      <td>${oauth_client.organization.short_name}</td>
      <td>${oauth_client.name}</td>
      <td><span class="client-credential">${oauth_client.client_id}</a></td>
      <td>
        <a class="client-credential click-to-view">${oauth_client.client_secret}</a>
      </td>
      <td>${oauth_client.redirect_uri}</td>
      <td>${u' / '.join(oauth_client.authorized_scope)}</td>
      <td>${h.term(oauth_client.valid_since, oauth_client.expire_at)}</td>
    </tr>
% endfor
  </tbody>
</table>
<input type="submit" name="doDelete" class="btn btn-danger" value="削除する" data-submit-confirmation-prompt="選択されたOAuthClientを削除します。よろしいですか?" />
</form>
<div id="modal-new-oauth-client" class="modal hide" role="dialog" aria-hidden="true">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
    <h3>OAuthClient 登録</h3>
  </div>
  <div class="modal-body">
    ${panel('oauth_clients.new')}
  </div>
  <div class="modal-footer">
    <button class="btn" data-dismiss="modal" aria-hidden="true">キャンセル</button>
    <button class="btn btn-primary submit">Client ID / Secretの生成</button>
  </div>
</div>
<script type="text/javascript">
(function ($submit) {
  $submit.click(function () {
    var $modalBody = $submit.closest('.modal').find('.modal-body');
    var $form = $modalBody.find('form');
    $.ajax({
      url: $form.attr('action'),
      type: 'POST',
      dataType: 'html',
      data: {
        organization_name: $form.find('select[name=organization_name]').val(),
        name: $form.find('input[name=name]').val(),
        redirect_uri: $form.find('input[name=redirect_uri]').val()
      },
      success: function () {
        location.reload();
      },
      error: function (xhr) {
        $modalBody.html(xhr.responseText);
      }
    });
  });
})($('#modal-new-oauth-client .submit'));
</script>
