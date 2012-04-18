<%inherit file='../../layout_2col.mako'/>
<%namespace name="fco" file="../../formcomponents.mako"/>
<%namespace name="nco" file="../../navcomponents.mako"/>
<%namespace name="mco" file="../../modelcomponents.mako"/>

<h2>image asset</h2>

<div class="row-fluid">
  <div class="span10">
    ${nco.breadcrumbs(
	    names=["Top", "Asset"], 
	    urls=[request.route_path("dashboard")]
	)}
  </div>
</div>

<div class="row">
  <ul class="nav nav-tabs">
	<li><a href="${request.route_path("asset_list")}">all</a></li>
    <li class="active"><a href="${request.route_path("asset_image_list")}">image</a></li>
  	<li><a href="${request.route_path("asset_movie_list")}">movie</a></li>
   	<li><a href="${request.route_path("asset_flash_list")}">flash</a></li>
  </ul>
</div>

<div class="row show-grid">
  <div class="span5">
	<h4>アセットの追加</h4>
  </div>
  <div class="span5">
	<h4>アセットの検索</h4>
  </div>

  <div class="span5">
	<form action="${request.route_path("asset_image_create")}" method="POST" enctype="multipart/form-data">
      ${fco.form_as_table_strict(form, ["filepath","title","tags","private_tags"])}
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> Create</button>
    </form>
  </div>

  
  <div class="span5">
	<form action="${request.route_path("asset_search_image")}" method="GET">
      ${fco.form_as_table_strict(search_form, ["created_by","updated_by","tags"])}
	  <button type="submit" class="btn btn-info"><i class="icon-cog icon-white"></i> Search</button>
    </form>
  </div>
</div>

<h4>登録済みのアセット一覧</h4>
${mco.model_list(assets, mco.asset_list, u"アセットは登録されていません")}
