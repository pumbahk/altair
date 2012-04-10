<%inherit file='../layout_2col.mako'/>

<h2>削除確認 ${topcotent['title']} (ID: ${topcotent['id']})</h2>

<div class="row-fluid">
  <div class="span10">
    ${nco.breadcrumbs(
	    names=["Top", "Topic", topic["title"], u"削除確認"],
	    urls=[request.route_path("dashboard"),
              request.route_path("topic_list"),
              request.route_path("topic", id=topic["id"]),
              ]
	)}
  </div>
</div>

<div class="row">
  <div class="alert alert-error">
	以下の内容のトピックを削除します。良いですか？
  </div>
  <div class="span5">
    <table class="table table-striped">
      <tr><th class="span2">タイトル</th>
        <td>${topic['title']}</td></tr>
      <tr><th class="span2">トピックの種別</th>
        <td>${topic["kind"]}</td></tr>
      <tr><th class="span2">公開開始日</th>
        <td>${topic["publish_open_on"]}</td></tr>
      <tr><th class="span2">公開終了日</th>
        <td>${topic["publish_close_on"]}</td></tr>
      <tr><th class="span2">内容</th>
        <td>${topic['text']|n}</td></tr>
      <tr><th class="span2">表示順序</th>
        <td>${topic["orderno"]}</td></tr>
      <tr><th class="span2">公開禁止</th>
        <td>${topic["is_vetoed"]}</td></tr>
      <tr><th class="span2">イベント以外のページ</th>
        <td>${topic["page"].title if topic["page"] else "-"}</td></tr>
      <tr><th class="span2">イベント</th>
        <td>${topic["event"].title if topic["event"] else "-"}</td></tr>
      <tr><th class="span2">全体に公開</th>
        <td>${topic["is_global"]}</td></tr>
    </table>
  </div>
  <div class="span6">
	<form action="${request.route_path("topic", id=topic["id"])}" method="POST">
 	  <input id="_method" name="_method" type="hidden" value="delete" />
	  <button type="submit" class="btn btn-danger"><i class="icon-trash icon-white"></i> Delete</button>
	</form>        
  </div>
</div>
