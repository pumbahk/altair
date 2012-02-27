<%inherit file='layout_2col.mako'/>
<div class="row">
    <div class="span6">
        <h4>お知らせ</h4>
        <table class="table table-striped">
            <tbody>
            <tr>
                <td>199x/1/23</td>
                <td>世界は核の炎に包まれた</td>
            </tr>
            <tr>
                <td>199x/1/23</td>
                <td>世界は核の炎に包まれた</td>
            </tr>
            </tbody>
        </table>
    </div>
    <div class="span4">
      <h4>イベント</h4>
      <div class="btn-toolbar">
        <div class="btn-group">
          <a class="btn btn-small" href="#">もうすぐ公開</a>
          <a class="btn btn-small" href="#">条件付き</a>
        </div>
      </div>
      <table class="table table-striped">
          %for event in events:
        <tr>
          <td>${event.event_open}</td><td><a href="${request.route_url("event", id=event.id)}">${event.title}</a></td>
        </tr>
          %endfor
      </table>
    </div>
</div>
