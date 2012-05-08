<%def name="model_list(objs, _model_list, failmessage)">
  %if objs:
     ${_model_list(objs)}
  %else:
     <div class="alert alert-info">
        ${failmessage}
    </div>
  %endif
</%def>

<%def name="event_list(objs)">
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
  </table>
</%def>

<%def name="topic_list(topics)">
<table class="table table-striped">
  <thead>
      <tr>
        <th>タイトル</th>
        <th>トピックの種別</th>
		<th>サブ分類</th>
        <th>公開開始日</th>
        <th>公開終了日</th>
        <th>内容</th>
        <th>表示順序</th>
        <th>公開禁止</th>
        <th>イベント以外のページ</th>
        <th>イベント</th>
        <th>全体に公開</th>
      </tr>
  </thead>
  <tbody>
  %for topic in topics:
    <tr>
      <td><a href="${request.route_path("topic", id=topic.id)}">${topic.title}</a></td>
      <td>${topic.kind}</td>
      <td>${topic.subkind}</td>
      <td>${topic.publish_open_on}</td>
      <td>${topic.publish_close_on}</td>
      <td>${topic.text if len(topic.text) <= 20 else topic.text[:20]+"..."}</td>
      <td>${topic.orderno}</td>
      <td>${topic.is_vetoed}</td>
      <td>${topic.page.title if topic.page else "-"}</td>
      <td>${topic.event.title if topic.event else "-"}</td>
      <td>${topic.is_global}</td>
    </tr>
  %endfor
  </tbody>
</table>
</%def>

<%def name="topcontent_list(topcontents)">
<table class="table table-striped">
      <thead>
      <tr>
        <th>タイトル</th>
        <th>種別</th>
		<th>サブ分類</th>
        <th>公開開始日</th>
        <th>公開終了日</th>
        <th>内容</th>
        <th>表示順序</th>
        <th>公開禁止</th>
        <th>ページ</th>
        <th>画像</th>
        <th>カウントダウンの種別</th>
      </tr>
      </thead>
  <tbody>
  %for topcontent in topcontents:
  <tr>
      <td><a href="${request.route_path("topcontent", id=topcontent['id'])}">${topcontent['title']}</a></td>
      <td>${topcontent["kind"]}</td>
      <td>${topcontent["subkind"]}</td>
      <td>${topcontent["publish_open_on"]}</td>
      <td>${topcontent["publish_close_on"]}</td>
      <td>${topcontent['text'] if len(topcontent['text']) <= 20 else topcontent['text'][:20]+"..."}</td>
      <td>${topcontent["orderno"]}</td>
      <td>${topcontent["is_vetoed"]}</td>
      <td>${topcontent["page"].title if topcontent["page"] else "-"}</td>
      <td><a href="${request.route_path("asset_display", asset_id=topcontent["image_asset"].id)}">${topcontent["image_asset"]}</a></td>
      <td>${topcontent["countdown_type" ]}</td>
  </tr>
  %endfor
  </tbody>
</table>
</%def>

<%def name="page_list(pages)">
<table class="table table-striped">
  <tbody>
    %for page in pages:
      <tr>
        <td>${page.created_at}</td>
        <td>${page.url}</td>
        <td><a href="${request.route_path("page_edit_", page_id=page.id)}">${page.title}</a></td>
        <td>
          <a href="${h.front.to_preview_page(request, page)}" class="btn btn-small"><i class="icon-eye-open"> </i> Preview</a>
        </td>
      </tr>
    %endfor
  </tbody>
</table>
</%def>

<%def name="asset_list(assets)">
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
              <td><a href="${request.route_path("asset_image_detail", asset_id=asset.id)}">${asset.title}</a></td>
              <td>${u",".join([x.label for x in asset.tags])}</td>
              <td>${asset.created_at}(${asset.created_by.screen_name})</td>
              <td>${asset.updated_at}(${asset.updated_by.screen_name})</td>
          </tr>
          %endfor
      </tbody>
  </table>
</%def>
