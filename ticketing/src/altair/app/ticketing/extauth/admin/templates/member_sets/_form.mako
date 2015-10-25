<div class="control-group">
  <label class="control-label" for="member_set-form--name">${form.name.label.text}</label>
  <div class="controls">
    ${form.name(id="member_set-form--name")}
    %if form.name.errors:
    <span class="help-inline">${u' / '.join(form.name.errors)}</span>
    % endif
  </div>
  <label class="control-label" for="member_set-form--display_name">${form.display_name.label.text}</label>
  <div class="controls">
    ${form.display_name(id="member_set-form--display_name")}
    %if form.display_name.errors:
    <span class="help-inline">${u' / '.join(form.display_name.errors)}</span>
    % endif
  </div>
  <label class="control-label" for="member_set-form--applicable_subtype">${form.applicable_subtype.label.text}</label>
  <div class="controls">
    ${form.applicable_subtype(id="member_set-form--applicable_subtype")}
    %if form.applicable_subtype.errors:
    <span class="help-inline">${u' / '.join(form.applicable_subtype.errors)}</span>
    % endif
  </div>
  <label class="control-label" for="member_set-form--use_password">${form.use_password.label.text}</label>
  <div class="controls">
    ${form.use_password(id="member_set-form--use_password")}
    %if form.use_password.errors:
    <span class="help-inline">${u' / '.join(form.use_password.errors)}</span>
    % endif
  </div>
  <label class="control-label" for="member_set-form--auth_identifier_field_name">${form.auth_identifier_field_name.label.text}</label>
  <div class="controls">
    ${form.auth_identifier_field_name(id="member_set-form--auth_identifier_field_name")}
    %if form.auth_identifier_field_name.errors:
    <span class="help-inline">${u' / '.join(form.auth_identifier_field_name.errors)}</span>
    % endif
  </div>
  <label class="control-label" for="member_set-form--auth_secret_field_name">${form.auth_secret_field_name.label.text}</label>
  <div class="controls">
    ${form.auth_secret_field_name(id="member_set-form--auth_secret_field_name")}
    %if form.auth_secret_field_name.errors:
    <span class="help-inline">${u' / '.join(form.auth_secret_field_name.errors)}</span>
    % endif
  </div>
</div>
