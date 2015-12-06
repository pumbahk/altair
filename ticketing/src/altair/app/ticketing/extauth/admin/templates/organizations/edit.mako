<%inherit file="/base.mako" />
<h2>オーガニゼーション編集</h2>
% for message in request.session.pop_flash():
<div class="alert">
  <button type="button" class="close" data-dismiss="alert">&times;</button>
  <strong>${message}</strong>
</div>
% endfor
<form id="organization-form" method="POST">
  <ul>
  % for msg in request.session.pop_flash():
    <li>${msg}</li>
  % endfor
  </ul>
  <%include file="_form.mako" />
  <button class="btn">編集</button>
  <a href="${request.route_path('top')}">戻る</a>
</form>
