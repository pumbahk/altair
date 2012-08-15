<%inherit file='../layout_2col.mako'/>
<%namespace name="nco" file="../navcomponents.mako"/>

<%block name="style">
<style type="text/css">
h3{ 
  margin-top:20px;
}
</style>
</%block>

<div class="row-fluid">
    ${nco.breadcrumbs(
        names=["Top", "Page", static_page.name],
        urls=[request.route_path("dashboard"), request.route_path("pageset_list", kind="static")]
    )}


<h2>${static_page.name}</h2>

<table class="table table-striped">
      <tr>
        <th class="span2">タイトル</th><td>${static_page.name}</td>
      </tr>
      <tr>
        <th>作成日時</th><td>${h.base.jdate(static_page.created_at)}</td>
      </tr>
      <tr>
        <th>更新日時</th><td>${h.base.jdate(static_page.updated_at)}</td>
      </tr>
    </table>

<div class="btn-group">
    <a class="btn do-post"
	   href="${request.route_path("static_page",action="delete",static_page_id=static_page.id)}">
      <i class="icon-trash"></i> 削除
    </a>
    <button class="btn dropdown-toggle" data-toggle="dropdown">
        <span class="caret"></span>
    </button>
    <ul class="dropdown-menu">
    </ul>
</div>
<hr/>

<h3>登録されているファイル</h3>
<div class="well">
  ${static_directory.link_tree_from_static_page(request,static_page)}
</div>

<h3>操作</h3>
<div class="row">
  <div class="span5">
	<div class="well" style="height:120px;">
	  <h4 style="margin-bottom:10px;">zipファイルにまとめてdownloadする</h4>
	  <a href="${request.route_path("static_page", action="download", static_page_id=static_page.id)}" class="btn">zipでdownload</a>
	</div>
  </div>

  <div class="span6">
	<div class="well" style="height:120px;">
	  <h4 style="margin-bottom:10px;">zipファイルでuploadし直す</h4>
	  <form class="form" action="${request.route_path("static_page", action="upload", static_page_id=static_page.id)}" 
			method="POST" enctype="multipart/form-data">
		<label>zipfile: <input id="zipfile" type="file" name="zipfile"/></label>
		<input class="btn" type="submit" value="zipでupload"/>
	  </form>
	</div>
  </div>
</div>

<script type="text/javascript">
  $(function(){
   $(".box .btn-group a.action").click(function(){
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
  $("a.do-post").click(function(){
    if(window.confirm("本当に登録されたデータを削除しますか?")){
	  $.post($(this).attr("href")).done(function(data){
		location.href = data["redirect_to"];
	  });
    }
    return false;
  });
 })
</script>

</div>
