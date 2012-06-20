<%def name="multiple_action_button(request, prefix)">
  <div class="btn-group">
	<a href="${request.route_path(prefix+"_update",action="input",id="__id__")}" class="btn">
	  <i class="icon-pencil"></i> 編集
	</a>
	<button class="btn dropdown-toggle" data-toggle="dropdown">
		<span class="caret"></span>
	</button>
	<ul class="dropdown-menu">
	  <li>
		<a href="${request.route_path(prefix+"_update",action="input",id="__id__")}">
		  <i class="icon-minus"></i> 編集
		</a>
	  </li>
	  <li>
		<a href="${request.route_path(prefix+"_create",action="input",id="__id__")}">
		  <i class="icon-minus"></i> 新規作成
		</a>
	  </li>
	  <li>
		<a href="${request.route_path(prefix+"_delete",action="confirm",id="__id__")}">
		  <i class="icon-minus"></i> 削除
		</a>
	  </li>
	</ul>
  </div>
</%def>

<%def name="multiple_action_button_script()">
<script type="text/javascript">
  $(function(){
   $(".box .btn-group a").click(function(){
	  var  pk = $(this).parents(".box").find("input[name='object_id']:checked").val();
	  if(!pk){ console.log("sorry"); return false; }

	  // initialize
	  var $this = $(this);
	  if (!$this.data("href-fmt")){
		$this.data("href-fmt", this.href);
	  }
	  this.href = $this.data("href-fmt").replace("__id__", pk);
	  return true;;
	});
  })
</script>
</%def>
