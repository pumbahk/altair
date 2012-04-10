<%inherit file='../layout_2col.mako'/>
<%namespace name="co" file="components.mako"/>
<%namespace name="nco" file="../navcomponents.mako"/>

<h2>複製確認画面 ページのタイトル - ${page.title} (ID: ${page.id})</h2>

<div class="row-fluid">
  <div class="span10">
    ${nco.breadcrumbs(
	    names=["Top", "Page", page.title, u"複製"], 
	    urls=[request.route_path("dashboard"),
              request.route_path("page"),
              h.page.to_edit_page(request,page)]
	)}
  </div>
</div>

<div class="row">
  <div class="alert">
	以下の内容のページを複製します。良いですか？
  </div>
  <div class="span5">
     ${co.page_description(page)}
  </div>
  <div class="span6">
	<form action="${h.page.to_duplicate(request,page)}" method="POST">
 	  <input id="_method" name="_method" type="hidden" value="post" />
	  <button type="submit" class="btn"><i class="icon-trash icon-white"></i> Duplicate</button>
	</form>        
  </div>
</div>
