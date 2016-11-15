<div class="control-group">
  <label class="control-label" for="host-form--organization_id">${form.organization_id.label.text}</label>
  <div class="controls">
    ${form.organization_id(id="host-form--organization_id")}
    %if form.organization_id.errors:
    <span class="help-inline">${u' / '.join(form.organization_id.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="host-form--name">${form.name.label.text}</label>
  <div class="controls">
    ${form.name(id="host-form--name")}
    %if form.name.errors:
    <span class="help-inline">${u' / '.join(form.name.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="host-form--display_name">${form.display_name.label.text}</label>
  <div class="controls">
    ${form.display_name(id="host-form--display_name")}
    %if form.display_name.errors:
    <span class="help-inline">${u' / '.join(form.display_name.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="host-form--auth_type">${form.auth_type.label.text}</label>
  <div class="controls">
    ${form.auth_type(id="host-form--auth_type")}
    %if form.auth_type.errors:
    <span class="help-inline">${u' / '.join(form.auth_type.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="host-form--endpoint_base">${form.endpoint_base.label.text}</label>
  <div class="controls">
    ${form.endpoint_base(id="host-form--endpoint_base")}
    %if form.endpoint_base.errors:
    <span class="help-inline">${u' / '.join(form.endpoint_base.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="host-form--consumer_key">${form.consumer_key.label.text}</label>
  <div class="controls">
    ${form.consumer_key(id="host-form--consumer_key")}
    %if form.consumer_key.errors:
    <span class="help-inline">${u' / '.join(form.consumer_key.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="host-form--consumer_secret">${form.consumer_secret.label.text}</label>
  <div class="controls">
    ${form.consumer_secret(id="host-form--consumer_secret")}
    %if form.consumer_secret.errors:
    <span class="help-inline">${u' / '.join(form.consumer_secret.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="host-form--scope">${form.scope.label.text}</label>
  <div class="controls">
    ${form.scope(id="host-form--scope")}
    %if form.scope.errors:
    <span class="help-inline">${u' / '.join(form.scope.errors)}</span>
    % endif
  </div>
</div>
