
<div class="control-group">
  <label class="control-label" for="operator-form--organization_id">${form.organization_id.label.text}</label>
  <div class="controls">
    % if request.operator.is_administrator and 'new' in request.path:
    ${form.organization_id(id="operator-form--organization_id")}
    % else:
    ${form.organization_id(id="operator-form--organization_id", disabled="True")}
    <input type="hidden" name="organization_id" value=${form.organization_id.data} />
    % endif
    %if form.organization_id.errors:
    <span class="help-inline">${u' / '.join(form.organization_id.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="operator-form--auth_identifier">${form.auth_identifier.label.text}</label>
  <div class="controls">
    ${form.auth_identifier(id="operator-form--auth_identifier")}
    %if form.auth_identifier.errors:
    <span class="help-inline">${u' / '.join(form.auth_identifier.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="operator-form--role_id">${form.role_id.label.text}</label>
  <div class="controls">
    ${form.role_id(id="operator-form--role_id")}
    %if form.role_id.errors:
    <span class="help-inline">${u' / '.join(form.role_id.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="operator-form--auth_secret">${form.auth_secret.label.text}</label>
  <div class="controls">
    ${form.auth_secret(id="operator-form--auth_secret", autocomplete="off")}
    %if form.auth_secret.errors:
    <span class="help-inline">${u' / '.join(form.auth_secret.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="operator-form--auth_secret_confirm">${form.auth_secret_confirm.label.text}</label>
  <div class="controls">
    ${form.auth_secret_confirm(id="operator-form--auth_secret_confirm", autocomplete="off")}
    %if form.auth_secret_confirm.errors:
    <span class="help-inline">${u' / '.join(form.auth_secret_confirm.errors)}</span>
    % endif
  </div>
</div>
