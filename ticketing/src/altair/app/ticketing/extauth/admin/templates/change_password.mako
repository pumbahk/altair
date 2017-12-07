<%inherit file="/base.mako" />

<style type="text/css">
    .error-msg-wrap {
        display: block;
        margin: 20px auto;
        width: 600px;
    }
    .error-msg-wrap ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    .error-msg-wrap ul li {
        font-size: 16px;
        font-weight: bold;
        color: #CF0000;
    }
    #login-form {
        margin-top: 30px;
        margin-bottom: 16px;
    }
    .spacer {
        width: 100px;
        margin: 0 auto;
    }
    .help-block {
      color: #CF0000;
      font-weight: bold;
    }
</style>

% if request.session.peek_flash():
<div class="error-msg-wrap">
<ul>
    % for msg in request.session.pop_flash():
    <li>${msg}</li>
    % endfor
</ul>
</div>
% endif
<div class="container" style="width: 600px;">
    <div class="page-header">
    <h1>パスワード変更</h1>
    </div>

    <div class="well">
        <form id="login-form" class="form-horizontal" action="${request.current_route_path(_query=request.GET)}" method="POST">
            ${form.csrf_token}
            <fieldset>
                <div class="control-group">
                    <label for="${form.old_password.id}" class="control-label">${form.old_password.label.text}</label>
                    <div class="controls">
                      ${form.old_password()}
                      % if form.old_password.errors:
                        % for error in form.old_password.errors:
                          <span class="help-block">${error}</span>
                        % endfor
                      % endif
                    </div>
                </div>
                <div class="control-group">
                    <label for="${form.password.id}" class="control-label">${form.password.label.text}</label>
                    <div class="controls">
                      ${form.password()}
                      % if form.password.errors:
                        % for error in form.password.errors:
                          <span class="help-block">${error}</span>
                        % endfor
                      % endif
                    </div>
                </div>
                <div class="control-group">
                    <label for="${form.password_confirm.id}" class="control-label">${form.password_confirm.label.text}</label>
                    <div class="controls">
                      ${form.password_confirm()}
                      % if form.password_confirm.errors:
                        % for error in form.password_confirm.errors:
                          <span class="help-block">${error}</span>
                        % endfor
                      % endif
                    </div>
                </div>
            </fieldset>
            <div class="spacer">
                <input class="btn btn-primary" type="submit" name="submit" value="ログイン">
            </div>
        </form>
    </div>
</div>

