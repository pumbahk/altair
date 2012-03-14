<%inherit file='../layout_2col.mako'/>

<div class="row-fluid">
  <div>
      <h4>イベント追加</h4>
      <%include file="parts/form.mako"/>
  </div>
</div>

<hr/>

<div class="row-fluid">
    <h4>イベント</h4>

    %if events:
        <table class="table table-striped">
            <thead>
            <tr>
                <th>イベント名</th>
                <th>開催場所</th>
                <th>公開日</th>
            </tr>
            </thead>
        <tbody>
        %for event in events['events']:
        <tr>
            <td><a href="${request.route_path("event", id=event['id'])}">${event['title']}</a></td>
            <td>${event['place']}</td>
            <td>${event['event_open']} - ${event['event_close']}</td>
        </tr>
        %endfor
        </tbody>
        </table>
    %else:
            <div class="alert alert-info">
                イベントは登録されていません。
            </div>
    %endif
</div>
