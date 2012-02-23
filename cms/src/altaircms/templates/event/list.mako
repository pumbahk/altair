<%inherit file='../layout_2col.mako'/>

<table class="table table-striped">
<thead>
  <tr>
    <th>イベント名</th>
    <th>開催場所</th>
    <th>公開日</th>
  </tr>
</thead>
<tbody>
%for event in events:
  <tr>
    <td><a href="/event/${event.id}">${event}</a></td>
    <td>${event.place}</td>
    <td>${event.event_open} - ${event.event_close}</td>
  </tr>
%endfor
</tbody>
</table>
