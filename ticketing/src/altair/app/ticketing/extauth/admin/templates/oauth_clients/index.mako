<%inherit file="/base.mako" />
<style type="text/css">
.text-danger {
  color: #A94442 !important;
  font-weight: bold;
}
.unknow-error-msgs span{
  display: block;
  font-weight: bold;
}
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
<h2>OAuthクライアント一覧</h2>
% if request.has_permission('manage_clients'):
  <button type="button" class="btn" onclick="create()" style="margin:10px 0;"><i class="icon-plus"></i>新規OAuthClient</button>
% endif
<form id="delete-form" action="${request.route_path('oauth_clients.delete')}" method="POST">

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
      <th>編集</th>
    </tr>
  </thead>
  <tbody>
% for oauth_client in oauth_clients:
    <tr>
      <td><input type="checkbox" name="id" value="${oauth_client.id}" /></td>
      <td><span>${oauth_client.organization.short_name}</span></td>
      <td><span id="client-name-${oauth_client.id}">${oauth_client.name}</span></td>
      <td><span id="client-credential-${oauth_client.id}">${oauth_client.client_id}</span></td>
      <td>
        <a class="client-credential click-to-view">${oauth_client.client_secret}</a>
      </td>
      <td><span id="client-redirect-uri-${oauth_client.id}">${oauth_client.redirect_uri}</span></td>
      <td>${u' / '.join(oauth_client.authorized_scope)}</td>
      <td><button type=button class="btn btn-small update-btn" onclick="update(${oauth_client.id})"><i class="icon-edit"></i></button></td>
    </tr>
% endfor
  </tbody>
</table>
<input type="submit" name="doDelete" class="btn btn-danger" value="削除する" data-submit-confirmation-prompt="選択されたOAuthClientを削除します。よろしいですか?" />
</form>
<div id="modal-oauth-client" class="modal hide" role="dialog" aria-hidden="true">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
    <h3>OAuthClient</h3>
  </div>
  <div class="modal-body">
    <form id="create-update-form" action="${request.route_path('oauth_clients.create_or_update')}" method="POST">
      <div class="unknow-error-msgs"></div>
      <input type="hidden" name="oauth_client_id" id="oauth_client_id" value="" />
      <div class="control-group">
        ${form.organization_id.label}
        % if request.operator.is_administrator:
        ${form.organization_id()}
        % else:
        ${form.organization_id(disabled="True")}
        <input type="hidden" name="organization_id" value=${form.organization_id.data} />
        % endif
      </div>
      <div class="control-group">
        ${form.name.label}
        ${form.name()}
      </div>
      <div class="control-group">
        ${form.redirect_uri.label}
        ${form.redirect_uri()}
      </div>
    </form>
  </div>
  <div class="modal-footer">
    <button type="button" class="btn" data-dismiss="modal" aria-hidden="true">キャンセル</button>
    <button type="button" class="btn btn-primary" onclick="submit_form()">Client ID / Secretの生成</button>
  </div>
</div>
<script type="text/javascript">
function reset() {
  var form = $('form#create-update-form');
  form.find("label").each(function() {$(this).removeClass("text-danger")});
  form.find("span").remove();
  form.find("input[name=name]").val("");
  form.find("input[name=redirect_uri]").val("");
  form.find("input[name=oauth_client_id]").val("");
}
function create() {
  reset();
  $('#modal-oauth-client').modal('show');
  return false;
}
function update(oauth_client_id) {
  reset();
  var form = $('form#create-update-form');
  form.find("input[name=name]").val($("#client-name-" + oauth_client_id).text());
  form.find("input[name=redirect_uri]").val($("#client-redirect-uri-" + oauth_client_id).text());
  form.find("input[name=oauth_client_id]").val(oauth_client_id);
  $('#modal-oauth-client').modal('show');
  return false;
}
function render_emsgs(emsgs) {
  for (var key in emsgs) {
      if (emsgs.hasOwnProperty(key)) {
        var msg = emsgs[key];
        if (key === "unknown-emsg") {
            $("div.unknow-error-msgs").append(
                ("<span class='alert alert-danger'>" + msg + "</span>")
            );
        } else {
          $("label[for=" + key + "]").addClass("text-danger");
          $("input[name=" + key + "]").after("<span class='help-inline text-danger'>" + msg + "</span>");
        }
      }
  }
}
function submit_form() {
  var form = $('form#create-update-form');
  var formdata = {
    "oauth_client_id": form.find('input[name=oauth_client_id]').val(),
    "organization_id": form.find('select[name=organization_id]').val(),
    "name": form.find('input[name=name]').val(),
    "redirect_uri": form.find('input[name=redirect_uri]').val()
  };
  $.ajax({
    url: form.attr('action'),
    type: 'POST',
    dataType: 'json',
    data: formdata,
    success: function() {
      location.reload();
    },
    error: function(xhr) {
      var responseText = JSON.parse(xhr.responseText);
      var emsgs = responseText['emsgs'] || xhr.statusText;
      render_emsgs(emsgs);
    }
  });
}
</script>
