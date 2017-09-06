<div class="control-group">
  <label class="control-label" for="oauth_service_provider-form--organization_id">${form.organization_id.label.text}</label>
  <div class="controls">
    % if request.operator.is_administrator and 'new' in request.path:
    ${form.organization_id(id="oauth_service_provider-form--organization_id")}
    % else:
    ${form.organization_id(id="oauth_service_provider-form--organization_id", disabled="True")}
    <input type="hidden" name="organization_id" value=${form.organization_id.data} />
    % endif
    %if form.organization_id.errors:
    <span class="help-inline">${u' / '.join(form.organization_id.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="oauth_service_provider-form--name">${form.name.label.text}</label>
  <div class="controls">
    ${form.name(id="oauth_service_provider-form--name")}
    %if form.name.errors:
    <span class="help-inline">${u' / '.join(form.name.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="oauth_service_provider-form--display_name">${form.display_name.label.text}</label>
  <div class="controls">
    ${form.display_name(id="oauth_service_provider-form--display_name")}
    %if form.display_name.errors:
    <span class="help-inline">${u' / '.join(form.display_name.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="oauth_service_provider-form--auth_type">${form.auth_type.label.text}</label>
  <div class="controls">
    ${form.auth_type(id="oauth_service_provider-form--auth_type")}
    %if form.auth_type.errors:
    <span class="help-inline">${u' / '.join(form.auth_type.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="oauth_service_provider-form--endpoint_base">${form.endpoint_base.label.text}</label>
  <div class="controls">
    ${form.endpoint_base(id="oauth_service_provider-form--endpoint_base")}
    %if form.endpoint_base.errors:
    <span class="help-inline">${u' / '.join(form.endpoint_base.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="oauth_service_provider-form--consumer_key">${form.consumer_key.label.text}</label>
  <div class="controls">
    ${form.consumer_key(id="oauth_service_provider-form--consumer_key")}
    %if form.consumer_key.errors:
    <span class="help-inline">${u' / '.join(form.consumer_key.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="oauth_service_provider-form--consumer_secret">${form.consumer_secret.label.text}</label>
  <div class="controls">
    ${form.consumer_secret(id="oauth_service_provider-form--consumer_secret")}
    %if form.consumer_secret.errors:
    <span class="help-inline">${u' / '.join(form.consumer_secret.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="oauth_service_provider-form--scope">${form.scope.label.text}</label>
  <div class="controls">
    ${form.scope(id="oauth_service_provider-form--scope")}
    %if form.scope.errors:
    <span class="help-inline">${u' / '.join(form.scope.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="oauth_service_provider-form--visible">${form.visible.label.text}</label>
  <div class="controls">
    ${form.visible(id="oauth_service_provider-form--visible")}
    %if form.visible.errors:
    <span class="help-inline">${u' / '.join(form.visible.errors)}</span>
    % endif
  </div>
</div>
