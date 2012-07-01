<div class="box">
${assets.all()}
  <table class="table">
	<thead>
	  <tr>
		<th>タイトル</th>
		<th>ファイル名</th>
		<th>登録日</th>
		<th>サイズ</th>
        <th>幅</th>
        <th>高さ</th>
	  </tr>
    </thead>
    <tbody>
<%doc>
  <%
  assets = list(assets)
  assetsize = len(assets)
  %>

     %for asset in assets:
     %endfor
</%doc>
  </tbody>
  </table>

</div>
