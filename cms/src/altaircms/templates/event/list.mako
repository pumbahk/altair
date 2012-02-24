<%inherit file='../layout_2col.mako'/>
<div class="row">
  <div class="span10">
  <h4>イベント追加</h4>
  <%include file="parts/form.mako"/>
  </div>
</div>

<hr/>

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
