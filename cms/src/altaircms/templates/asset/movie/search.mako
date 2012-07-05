<%inherit file='../../layout_2col.mako'/>
<%namespace name="fco" file="../../formcomponents.mako"/>
<%namespace name="nco" file="../../navcomponents.mako"/>
<%namespace name="mco" file="../../modelcomponents.mako"/>

<h2>movie asset 検索結果()</h2>

<div class="row-fluid">
  <div class="span10">
    ${nco.breadcrumbs(
	    names=["Top", "movieAsset", "search"], 
	    urls=[request.route_path("dashboard"),
              request.route_path("asset_movie_list")]
	)}
  </div>
</div>

<div class="row">
  <ul class="nav nav-tabs">
	<li><a href="${request.route_path("asset_list")}">all</a></li>
    <li><a href="${request.route_path("asset_image_list")}">image</a></li>
  	<li class="active"><a href="${request.route_path("asset_movie_list")}">movie</a></li>
   	<li><a href="${request.route_path("asset_flash_list")}">flash</a></li>
  </ul>
</div>

<div class="row show-grid">
	<h4>アセットの検索</h4>

	<form action="${request.route_path("asset_search_movie")}" method="GET">
      ${fco.formfield(search_form, "created_by")}
      ${fco.formfield(search_form, "updated_by")}
      ${fco.formfield(search_form, "tags")}
	  <button type="submit" class="btn btn-info"><i class="icon-cog icon-white"></i> Search</button>
    </form>
</div>

<h4>登録済みのアセット一覧</h4>
${mco.model_list(search_result, lambda xs,: mco.asset_list(xs, "asset_movie_detail"), u"アセットは登録されていません")}
