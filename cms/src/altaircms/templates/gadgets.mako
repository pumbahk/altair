<%def name="multiple_action_button(request, prefix)">
  <div class="btn-group">
	<a href="${request.route_path(prefix+"_update",action="input",id="__id__")}" class="btn action">
	  <i class="icon-pencil"></i> 編集
	</a>
	<button class="btn dropdown-toggle" data-toggle="dropdown">
		<span class="caret"></span>
	</button>
	<ul class="dropdown-menu">
	  <li>
		<a href="${request.route_path(prefix+"_update",action="input",id="__id__")}"  class="action">
		  <i class="icon-minus"></i> 編集
		</a>
	  </li>
	  <li>
		<a href="${request.route_path(prefix+"_create",action="input")}">
		  <i class="icon-minus"></i> 新規作成
		</a>
	  </li>
	  <li>
		<a href="${request.route_path(prefix+"_delete",action="confirm",id="__id__")}"  class="action">
		  <i class="icon-minus"></i> 削除
		</a>
	  </li>
	</ul>
  </div>
</%def>

<%def name="getti_update_code_button()">
  <a data-toggle="modal" href="#myModal" >
    <i class="icon-minus"></i>getti パフォーマンスコードの登録
  </a>
</%def>

<%def name="getti_update_code(performances,submit_id)">
  <div class="modal hide big-modal" id="myModal">
	<div class="modal-header">
	  <button type="button" class="close" data-dismiss="modal">×</button>
	  <h3>Getti パフォーマンスコードの登録</h3>
	</div>
	<div class="modal-body">
	  <pre>
登録コード: NTROS1007Z のとき
  * pcサイト購入リンク: 
  　https://www.e-get.jp/tstar/pt/&s=NTROS1007Z   
  * mobileサイト購入リンク:
  　https://www.e-get.jp/tstar/mt/&s=NTROS1007Z
を設定します
	  </pre>

	  <br/>

	  <table id="getti_code_tables">
		<thead><tr><th></th><th>公演名</th><th>バックエンドID</th><th>公演日時</th><th>場所</th><th>設定済み</th><th>登録コード</th></tr>
		</thead>
		<tbody>
		  %for p in  performances:
		  <tr>
			<td>${p.title}</td><td>${p.backend_id}</td><td>${h.base.jdate(p.start_on)}</td><td>${p.venue}</td>
			<td>${"y" if p.purchase_link or p.mobile_purchase_link else "n"}</td>
			<td><input name="p:${p.id}"></td>
		  </tr>
		  %endfor
		</tbody>
	  </table>
	</div>

	<div class="modal-footer">
	  <a href="#" class="btn" data-dismiss="modal">Close</a>
	  <button id="getti_submit" class="btn btn-primary">購入リンクを登録</button>
	</div>
  </div>

  ## js
  <script type="text/javascript">
	$("#${submit_id}").click(function(){
       var params = {};
	  $.each($("#getti_code_tables input"),function(i,e){
         var $this = $(e);
         if($this.val() != ""){
　　　	     params[$this.attr("name")] = $this.val();
	　　　}
       });
      var url = "${request.route_path("event_update", id=event.id, action="getti")}";
      // slackoff
      $.post(url, params).done(function(){location.reload();});
	return false;
	});
  </script>
</%def>
