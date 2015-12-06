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
  <label class="control-label" for="operator-form--role">${form.role.label.text}</label>
  <div class="controls">
    ${form.role(id="operator-form--role")}
    %if form.role.errors:
    <span class="help-inline">${u' / '.join(form.role.errors)}</span>
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
