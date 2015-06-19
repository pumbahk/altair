<%inherit file="/_base.mako" />
<%block name="title">ログイン</%block>
<form action="${request.current_route_path(_query=dict(return_url=return_url))}" method="POST">
  <div class="form-field">
    ${form.user_name.label}
    ${form.user_name()}
    ${form.user_name.errors}
  </div>
  <div class="form-field">
    ${form.password.label}
    ${form.password()}
    ${form.password.errors}
  </div>
  <input type="submit" value="ログイン" />
</form>
