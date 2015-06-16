<%inherit file="/_base.mako" />
<h1>案内画面2</h1>
<div>
  % if message is not None:
  <h2>案内メッセージ</h2> 
  <p>${message}</p>
  % else:
  <p>案内メッセージはありません</p>
  % endif
  % if continuable:
  % if auth_number_required:
  <a href="${request.route_path('service.reserved.inquiry')}"></a>
  % else:
  <a href="${request.route_path('service.reserved.entry')}">予約番号の入力に進む</a>
  % endif
  % endif
</div>
