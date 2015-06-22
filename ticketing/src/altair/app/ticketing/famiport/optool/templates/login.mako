<%inherit file="/_base.mako" />
<%block name="title">ログイン</%block>
<style>
    body {
        background-color: #eee;
    }
</style>

<form class="form-signin" action="${request.current_route_path(_query=dict(return_url=return_url))}" method="POST">
    <h2 class="form-signin-heading">プレイガイド様名</h2>
    <div class="form-group">
      ${form.user_name.label}
      ${form.user_name(class_='form-control',placeholder='ID')}
      % if form.user_name.errors:
        ${form.user_name.errors}
      % endif
      ${form.password.label}
      ${form.password(class_='form-control',placeholder='password')}
      % if form.user_name.errors:
        ${form.password.errors}
      % endif
    </div>
    <button type="submit" class="btn btn-lg btn-primary btn-block">Sign in</button>
</form>
