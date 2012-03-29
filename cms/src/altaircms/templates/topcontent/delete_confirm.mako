<%inherit file='../layout_2col.mako'/>

<div class="row" style="margin-bottom: 9px">
  <h2 class="span6">削除確認画面 トピックのタイトル - ${topcontent['title']} (ID: ${topcontent['id']})</h2>
</div>

<div class="row">
  <div class="alert alert-error">
	以下の内容のトピックを削除します。良いですか？
  </div>
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
		<tr><th class="span2">ページ</th>
		  <td>${topcontent["page"].title if topcontent["page"] else "-"}</td></tr>
		<tr><th class="span2">画像</th>
		  <td>${topcontent["image_asset"]}</td></tr>
		<tr><th class="span2">カウントダウンの種別</th>
		  <td>${topcontent["countdown_type"]}</td></tr>
    </table>
  </div>
  <div class="span6">
	<form action="${request.route_path("topcontent", id=topcontent["id"])}" method="POST">
 	  <input id="_method" name="_method" type="hidden" value="delete" />
	  <button type="submit" class="btn btn-danger"><i class="icon-trash icon-white"></i> Delete</button>
	</form>        
  </div>
</div>
