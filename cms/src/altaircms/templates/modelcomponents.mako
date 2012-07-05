<%def name="model_list(objs, _model_list, failmessage)">
  %if objs:
     ${_model_list(objs)}
  %else:
     <div class="alert alert-info">
        ${failmessage}
    </div>
  %endif
</%def>

<%def name="event_list(events)">
  <table class="table table-striped">
    <thead>
    <tr>
        <th>イベント名</th>
        <th>公演数</th>
        <th>公開日</th>
        <th>検索対象に含める</th>
    </tr>
    </thead>
    <tbody>
    %for event in events:
      <tr>
        <td><a href="${request.route_path("event", id=event.id)}">${event.title}</a></td>
        <td>${len(event.performances)}</td>
        <td>${event.event_open} - ${event.event_close}</td>
		<td>${event.is_searchable}</td>
<%doc>
		<td>
		  <a href="${request.route_path("event_update",action="input",id=event.id)}" class="btn btn-small btn-primary">
			<i class="icon-cog icon-white"> </i> Update
		  </a>
		  <a href="${request.route_path("event_delete",action="confirm",id=event.id)}" class="btn btn-small btn-danger">
			<i class="icon-trash icon-white"> </i> Delete
		  </a>
		</td>
</%doc>
      </tr>
    %endfor
  </table>
</%def>

<%def name="page_list(pages)">
<table class="table table-striped">
  <tbody>
    %for page in pages:
      <tr>
        <td>${page.created_at}</td>
        <td><a href="${request.route_path("page_edit_", page_id=page.id)}">${page.name}</a></td>
        <td>${page.url}</td>
        <td>
          <a href="${h.link.preview_page_from_page(request, page)}" class="btn btn-small"><i class="icon-eye-open"> </i> Preview</a>
        </td>
      </tr>
    %endfor
  </tbody>
</table>
</%def>

<%def name="asset_list(assets,route_name)">
  <table class="table table-striped">
      <thead>
      <tr>
		<th>type</th>
		<th>タイトル</th>
        <th>タグ</th>
		<th>作成日時</th>
		<th>更新日時</th>
      </tr>
      </thread>
      <tbody>
          %for asset in assets:
          <tr>
              <td>${asset.discriminator}</td>
              <td><a href="${request.route_path(route_name, asset_id=asset.id)}">${asset.title}</a></td>
              <td>${u",".join([x.label for x in asset.tags])}</td>
              <td>${asset.created_at}(${asset.created_by.screen_name})</td>
              <td>${asset.updated_at}(${asset.updated_by.screen_name})</td>
          </tr>
          %endfor
      </tbody>
  </table>
</%def>
