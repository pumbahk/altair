<%inherit file='../layout_2col.mako'/>
<%namespace name="nco" file="../navcomponents.mako"/>
<%namespace name="fco" file="../formcomponents.mako"/>
<%namespace name="mco" file="../modelcomponents.mako"/>

<h2>${topic['title']} (ID: ${topic['id']})</h2>

<div class="row-fluid">
  <div class="span10">
    ${nco.breadcrumbs(
	    names=["Top", "Topic", topic["title"]],
	    urls=[request.route_path("dashboard"), request.route_path("topic_list")]
	)}
  </div>
</div>


<div class="row-fluid">
  <div class="span5">
  <h4>トピック</h4>
    <table class="table table-striped">
      <tr><th>タイトル</th>
        <td><a href="${request.route_path("topic", id=topic['id'])}">${topic['title']}</a></td></tr>
      <tr><th>トピックの種別</th>
        <td>${topic["kind"]}</td></tr>
      <tr><th>サブ分類</th>
        <td>${topic["subkind"]}</td></tr>
      <tr><th>公開開始日</th>
        <td>${topic["publish_open_on"]}</td></tr>
      <tr><th>公開終了日</th>
        <td>${topic["publish_close_on"]}</td></tr>
      <tr><th>内容</th>
        <td>${topic['text']|n}</td></tr>
      <tr><th>表示順序</th>
        <td>${topic["orderno"]}</td></tr>
      <tr><th>公開禁止</th>
        <td>${topic["is_vetoed"]}</td></tr>
      <tr><th>イベント以外のページ</th>
        <td>${topic["page"].title if topic["page"] else "-"}</td></tr>
      <tr><th>イベント</th>
        <td>${topic["event"].title if topic["event"] else "-"}</td></tr>
      <tr><th>全体に公開</th>
        <td>${topic["is_global"]}</td></tr>
    </table>
  </div>

  <div class="span6">
    <a class="btn btn-success" href=""><i class="icon-eye-open"> </i> Preview</a>
    <a class="btn btn-danger" href="${request.route_path("topic_delete_confirm",id=topic["id"])}"><i class="icon-trash icon-white"></i> Delete</a>
	<a class="btn btn-primary" href="${request.route_path("topic_update_confirm",id=topic["id"])}"><i class="icon-cog"></i> Settings</a>
    <a class="btn" href=""><i class="icon-refresh"> </i> Sync</a>
  </div>
</div>
