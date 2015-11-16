<div class="control-group">
  <label class="control-label" for="organization-form--maximum_oauth_scope">${form.maximum_oauth_scope.label.text}</label>
  <div class="controls">
    ${form.maximum_oauth_scope(id="organization-form--maximum_oauth_scope")}
    %if form.maximum_oauth_scope.errors:
    <span class="help-inline">${u' / '.join(form.maximum_oauth_scope.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="organization-form--maximum_oauth_client_expiration_time">${form.maximum_oauth_client_expiration_time.label.text}</label>
  <div class="controls">
    ${form.maximum_oauth_client_expiration_time(id="organization-form--maximum_oauth_client_expiration_time")}
    %if form.maximum_oauth_client_expiration_time.errors:
    <span class="help-inline">${u' / '.join(form.maximum_oauth_client_expiration_time.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="organization-form--canonical_host_name">${form.canonical_host_name.label.text}</label>
  <div class="controls">
    ${form.canonical_host_name(id="organization-form--canonical_host_name")}
    %if form.canonical_host_name.errors:
    <span class="help-inline">${u' / '.join(form.canonical_host_name.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="organization-form--invalidate_client_http_session_on_access_token_revocation">${form.invalidate_client_http_session_on_access_token_revocation.label.text}</label>
  <div class="controls">
    ${form.invalidate_client_http_session_on_access_token_revocation(id="organization-form--invalidate_client_http_session_on_access_token_revocation")}
    %if form.invalidate_client_http_session_on_access_token_revocation.errors:
    <span class="help-inline">${u' / '.join(form.invalidate_client_http_session_on_access_token_revocation.errors)}</span>
    % endif
  </div>
</div>
<fieldset>
<legend>楽天会員認証の設定</legend>
<div class="control-group">
  <label class="control-label" for="organization-settings-rakuten_auth-form--oauth_consumer_key">${form.settings.rakuten_auth.oauth_consumer_key.label.text}</label>
  <div class="controls">
    ${form.settings.rakuten_auth.oauth_consumer_key(id="organization-settings-rakuten_auth-form--oauth_consumer_key")}
    %if form.settings.rakuten_auth.oauth_consumer_key.errors:
    <span class="help-inline">${u' / '.join(form.settings.rakuten_auth.oauth_consumer_key.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="organization-settings-rakuten_auth-form--oauth_consumer_secret">${form.settings.rakuten_auth.oauth_consumer_secret.label.text}</label>
  <div class="controls">
    ${form.settings.rakuten_auth.oauth_consumer_secret(id="organization-settings-rakuten_auth-form--oauth_consumer_secret")}
    %if form.settings.rakuten_auth.oauth_consumer_secret.errors:
    <span class="help-inline">${u' / '.join(form.settings.rakuten_auth.oauth_consumer_secret.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="organization-settings-rakuten_auth-form--proxy_url_pattern">${form.settings.rakuten_auth.proxy_url_pattern.label.text}</label>
  <div class="controls">
    ${form.settings.rakuten_auth.proxy_url_pattern(id="organization-settings-rakuten_auth-form--proxy_url_pattern")}
    %if form.settings.rakuten_auth.proxy_url_pattern.errors:
    <span class="help-inline">${u' / '.join(form.settings.rakuten_auth.proxy_url_pattern.errors)}</span>
    % endif
  </div>
</div>
</fieldset>
