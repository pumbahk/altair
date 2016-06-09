<%inherit file="../base.mako" />
<div class="container">
<h2>案件を選択</h2>
<ul>
% for event in _context.events:
  <li><a href="${request.path}${event.id}">${event.title}</a></li>
% endfor
</ul>
</div>
