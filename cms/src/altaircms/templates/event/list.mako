<%inherit file='../layout.mako'/>

<h1>イベント一覧</h1>

<hr/>

<ul>
%for event in events:
<li><a href="/event/${event.id}">${event}</a></li>
%endfor
</ul>
