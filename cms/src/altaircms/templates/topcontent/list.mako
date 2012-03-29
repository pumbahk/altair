<%inherit file='../layout_2col.mako'/>

<div class="row-fluid">
  <div>
      <h4>トップコンテンツ追加</h4>
      <%include file="parts/form.mako"/>
  </div>
</div>

<hr/>

<div class="row-fluid">
    <h4>トップコンテンツ</h4>

    %if topcontents:
        <table class="table table-striped">
            <thead>
            <tr>
              <th>タイトル</th>
              <th>種別</th>
              <th>公開開始日</th>
              <th>公開終了日</th>
              <th>内容</th>
              <th>表示順序</th>
              <th>公開禁止</th>
              <th>イベント</th>
              <th>画像</th>
              <th>カウントダウンの種別</th>
            </tr>
            </thead>
        <tbody>
        %for topcontent in topcontents['topcontents']:
        <tr>
            <td><a href="${request.route_path("topcontent", id=topcontent['id'])}">${topcontent['title']}</a></td>
            <td>${topcontent["kind"]}</td>
            <td>${topcontent["publish_open_on"]}</td>
            <td>${topcontent["publish_close_on"]}</td>
            <td>${topcontent['text'] if len(topcontent['text']) <= 20 else topcontent['text'][:20]+"..."}</td>
            <td>${topcontent["orderno"]}</td>
            <td>${topcontent["is_vetoed"]}</td>
            <td>${topcontent["event"].title if topcontent["event"] else "-"}</td>
            <td><a href="${request.route_path("asset_view", asset_id=topcontent["image_asset"].id)}">${topcontent["image_asset"]}</a></td>
			<td>${topcontent["countdown_type" ]}</td>
        </tr>
        %endfor
        </tbody>
        </table>
    %else:
		<div class="alert alert-info">
			トップコンテンツは登録されていません。
		</div>
    %endif
</div>
