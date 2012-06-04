<%inherit file='../layout_2col.mako'/>
<%namespace name="fco" file="../formcomponents.mako"/>
<%namespace name="nco" file="../navcomponents.mako"/>

<h2>asset</h2>

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
	<li class="active"><a href="${request.route_path("asset_list")}">all</a></li>
	<li ><a href="${request.route_path("asset_image_list")}">image</a></li>
	<li><a href="${request.route_path("asset_movie_list")}">movie</a></li>
	<li><a href="${request.route_path("asset_flash_list")}">flash</a></li>
  </ul>
</div>

<div class="row">
  <div class="span6">
    ## image asset
    <h4>画像アセットの追加</h4>
	<form action="${request.route_path("asset_image_create")}" method="POST" enctype="multipart/form-data">
      ${fco.form_as_table_strict(image_asset_form, ["filepath","title","tags","private_tags"])}
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> Create</button>
    </form>

    ## movie asset
    <h4>動画アセットの追加</h4>
	<form action="${request.route_path("asset_movie_create")}" method="POST" enctype="multipart/form-data">
      ${fco.form_as_table_strict(movie_asset_form, ["filepath","title","placeholder","tags","private_tags"])}
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> Create</button>
    </form>

    ## flash asset
    <h4>flashアセットの追加</h4>
	<form action="${request.route_path("asset_flash_create")}" method="POST" enctype="multipart/form-data">
      ${fco.form_as_table_strict(flash_asset_form, ["filepath","title","placeholder","tags","private_tags"])}
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> Create</button>
    </form>

  </div>
</div>

<%
seq = h.paginate(request, assets, item_count=assets.count())
%>

<h4>登録済みのアセット一覧</h4>
${seq.pager()}
<table class="table table-striped">
    <tbody>
        %for asset in seq.paginated():
        <tr>
            <td>${asset.created_at}</td>
            <td>${asset.discriminator}</td>
            <td><a href="${request.route_path("asset_detail", asset_type=asset.discriminator, asset_id=asset.id)}">${asset}</a></td>
        </tr>
        %endfor
    </tbody>
</table>
${seq.pager()}
