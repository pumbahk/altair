<%inherit file="/base.mako" />
<h2>新規Host作成</h2>
% for message in request.session.pop_flash():
<div class="alert">
  <button type="button" class="close" data-dismiss="alert">&times;</button>
  <strong>${message}</strong>
</div>
% endfor
<form id="host-form" method="POST">
  <ul>
  % for msg in request.session.pop_flash():
    <li>${msg}</li>
  % endfor
  </ul>
  <div class="control-group">
    <label class="control-label" for="host-form--host_name">${form.host_name.label.text}</label>
    <div class="controls">
      ${form.host_name(id="host-form--host_name")}
      %if form.host_name.errors:
      <span class="help-inline">${u' / '.join(form.host_name.errors)}</span>
      % endif
    </div>
  </div>
  <button class="btn">作成</button>
  <a href="${request.route_path('top')}">戻る</a>
</form>
