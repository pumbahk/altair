<%inherit file='../layout_2col.mako'/>

<div class="row" style="margin-bottom: 9px">
  <h2 class="span6">トピックのタイトル - ${topic['title']} (ID: ${topic['id']})</h2>
  <div class="span4">
    <a class="btn" href="${request.route_url("page_add", topic_id=topic['id'])}"><i class="icon-plus"> </i> ページ追加</a>
    <a class="btn" href=""><i class="icon-eye-open"> </i> Preview</a>
    <a class="btn" href=""><i class="icon-refresh"> </i> Sync</a>
  </div>
</div>

<div class="row">
  <div class="span5">
    <table class="table table-striped">
      <tr>
        <th class="span2">タイトル</th><td>${topic['title']}</td>
      </tr>
      <tr>
        <th>関連イベント</th><td>${topic['event']}</td>
      </tr>
      <tr>
        <th class="span2">内容</th><td>${topic['text']}</td>
      </tr>
    </table>
  </div>
</div>
