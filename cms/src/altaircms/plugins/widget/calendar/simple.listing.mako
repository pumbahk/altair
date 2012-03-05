<div class="calendar-widget">
<ul>
%for p in performances:
  <li>
	<span>${p.title}(${p.performance_open.strftime("%m/%d")})</span>
	<a href="${p.event_id}">${p.event_id}</a>
	${p.performance_open.strftime("%H:%M")} 〜 ${p.performance_close.strftime("%H:%M")}
  </li>
%endfor
</ul>
</div>