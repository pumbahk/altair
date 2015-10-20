<form action="${request.route_path('oauth_clients.new')}" method="POST" onsubmit="return false;">
  <div class="control-group">
    ${form.name.label}
    ${form.name()}
    <span class="help-inline">${u' / '.join(form.name.errors)}</span>
  </div>
  <div class="control-group">
    ${form.redirect_uri.label}
    ${form.redirect_uri()}
    <span class="help-inline">${u' / '.join(form.redirect_uri.errors)}</span>
  </div>
</form>
