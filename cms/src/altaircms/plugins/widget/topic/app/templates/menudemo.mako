<html>
  <head> 
	<script type="text/javascript" src="/demo/static/js/backbone-patch.js"></script>
	<script type="text/javascript" src="/demo/static/js/backbone-localstorage.js"></script>
	<!-- <script type="text/javascript" src="/demo/static/js/demo.js"></script> -->
	<script type="text/javascript" src="/demo/static/js/lib.js"></script>
	<body>
	  <div id="app">
		<div class="title">
		  <h1>メニュータブ</h1>
		</div>
		<div class="content" class="float">
		  <div id="create-menu">
			<table>
	  		  <tr>
				<td><label>リンク先名<input id="label_input" placeholder="ここにリンク名を追加" type="text" /></label></td>
	  			<td><label>URL<input id="link_input" placeholder="ここにリンク先のURLを追加" type="text" /></label></td>
			  </tr>
			</table>
		  </div>
		  <span class="clear"/>

		  <h3>現在保存されているタブ</h3>
		  <hr/>

		  <div id="menus">
			<table>
			  <thead>
				<tr><th>リンク先名</th><th>URL</th><th>削除</th></tr>
			  </thead>
			  <tbody id="menulist">
			  </tbody>
			</table>
		  </div>
		</div>
		<button id="submit" type="button">登録</button>
	  </div>
	</body>
</html>
