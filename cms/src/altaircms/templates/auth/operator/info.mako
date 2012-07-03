<%inherit file='../../layout_2col.mako'/>

<a href="#" onclick="history.back(); return false;">戻る</a>
<h3>オペレータ情報</h3>

<table class="table">
  <tbody>
	<tr>
	  <tr><th>名前</th><td>${operator.screen_name}</td></tr>
	  <tr><th>Id</th><td>${operator.id }</td></tr>
	  <tr><th>所属組織</th><td>${organization.name }</td></tr>
	  <tr><th>バックエンド source</th><td>${operator.auth_source}</td></tr>
	  <tr><th>バックエンドId</th><td>${operator.user_id  }</td></tr>
	</tr>
  </tbody>
</table>
<a href="#" onclick="history.back(); return false;">戻る</a>
