<%inherit file='../layout_2col.mako'/>

<div class="row" style="margin-bottom: 9px">
  <h2 class="span6">トピックのタイトル - ${topcontent['title']} (ID: ${topcontent['id']})</h2>
  <div class="span4">
    <a class="btn btn-success" href=""><i class="icon-eye-open"> </i> Preview</a>
    <a class="btn btn-danger" href="${request.route_path("topcontent_delete_confirm",id=topcontent["id"])}"><i class="icon-trash icon-white"></i> Delete</a>
	<a class="btn btn-primary" href="${request.route_path("topcontent_update_confirm",id=topcontent["id"])}"><i class="icon-cog"></i> Settings</a>
    <a class="btn" href=""><i class="icon-refresh"> </i> Sync</a>
  </div>
</div>

<div class="row">
  <div class="span5">
    <table class="table table-striped">
        <tr><th class="span2">タイトル</th>
          <td><a href="${request.route_path("topcontent", id=topcontent['id'])}">${topcontent['title']}</a></td></tr>
		<tr><th class="span2">種別</th>
		  <td>${topcontent["kind"]}</td></tr>
		<tr><th class="span2">公開開始日</th>
		  <td>${topcontent["publish_open_on"]}</td></tr>
		<tr><th class="span2">公開終了日</th>
		  <td>${topcontent["publish_close_on"]}</td></tr>
		<tr><th class="span2">内容</th>
		  <td>${topcontent['text']}</td></tr>
		<tr><th class="span2">表示順序</th>
		  <td>${topcontent["orderno"]}</td></tr>
		<tr><th class="span2">公開禁止</th>
		  <td>${topcontent["is_vetoed"]}</td></tr>
		<tr><th class="span2">イベント</th>
		  <td>${topcontent["event"].title if topcontent["event"] else "-"}</td></tr>
		<tr><th class="span2">画像</th>
		  <td>${topcontent["image_asset"]}</td></tr>
		<tr><th class="span2">カウントダウンの種別</th>
		  <td>${topcontent["countdown_type"]}</td></tr>
    </table>
  </div>
</div>
