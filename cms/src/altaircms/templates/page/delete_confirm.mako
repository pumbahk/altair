<%inherit file='../layout_2col.mako'/>
<%namespace name="co" file="components.mako"/>

<div class="row" style="margin-bottom: 9px">
  <h2 class="span6">削除確認画面 トピックのタイトル - ${page.title} (ID: ${page.id})</h2>
</div>

<div class="row">
  <div class="alert alert-error">
	以下の内容のページを削除します。良いですか？
  </div>
  <div class="span5">
     ${co.page_description(page)}
  </div>
  <div class="span6">
	<form action="${h.page.to_delete(request,page)}" method="POST">
 	  <input id="_method" name="_method" type="hidden" value="delete" />
	  <button type="submit" class="btn btn-danger"><i class="icon-trash icon-white"></i> Delete</button>
	</form>        
  </div>
</div>
