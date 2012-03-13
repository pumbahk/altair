<%inherit file='../layout_2col.mako'/>

<div class="row" style="margin-bottom: 9px">
  <h2 class="span6">削除確認画面 トピックのタイトル - ${topic['title']} (ID: ${topic['id']})</h2>
</div>

<div class="row">
  <div class="alert alert-error">
	以下の内容のトピックを削除します。良いですか？
  </div>
  <div class="span5">
    <table class="table table-striped">
      <tr>
        <th class="span2">タイトル</th><td>${topic['title']}</td>
      </tr>
      <tr>
        <th>トピックの種類</th><td>${topic['kind']}</td>
      </tr>
      <tr>
        <th>公開日</th><td>${topic['publish_at']}</td>
      </tr>
      <tr>
        <th class="span2">内容</th><td>${topic['text']|n}</td>
      </tr>
    </table>
  </div>
  <div class="span6">
	<form action="${request.route_url("topic", id=topic["id"])}" method="POST">
 	  <input id="_method" name="_method" type="hidden" value="delete" />
	  <button type="submit" class="btn btn-danger"><i class="icon-trash icon-white"></i> Delete</button>
	</form>        
  </div>
</div>
