<%inherit file='../layout_2col.mako'/>
<%namespace name="fco" file="../formcomponents.mako"/>
<<<<<<< HEAD
=======
<%namespace name="nco" file="../navcomponents.mako"/>
>>>>>>> refine template. add required mark

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
  <h4>アセットの追加</h4>

  <div class="span6">
    ## image asset
	<form action="${request.route_path("asset_image_create")}" method="POST" enctype="multipart/form-data">
      ${fco.formfield(image_asset_form, "filepath")}
      ${fco.formfield(image_asset_form, "tags")}
      ${fco.formfield(image_asset_form, "private_tags")}
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> Create</button>
    </form>

    ## movie asset
	<form action="${request.route_path("asset_movie_create")}" method="POST" enctype="multipart/form-data">
      ${fco.formfield(movie_asset_form, "filepath")}
      ${fco.formfield(movie_asset_form, "placeholder")}
      ${fco.formfield(movie_asset_form, "tags")}
      ${fco.formfield(movie_asset_form, "private_tags")}
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> Create</button>
    </form>

    ## flash asset
	<form action="${request.route_path("asset_flash_create")}" method="POST" enctype="multipart/form-data">
      ${fco.formfield(flash_asset_form, "filepath")}
      ${fco.formfield(movie_asset_form, "placeholder")}
      ${fco.formfield(flash_asset_form, "tags")}
      ${fco.formfield(flash_asset_form, "private_tags")}
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> Create</button>
    </form>

  </div>
</div>

<h4>登録済みのアセット一覧</h4>
<table class="table table-striped">
    <tbody>
        %for asset in assets:
        <tr>
            <td>${asset.created_at}</td>
            <td>${asset.discriminator}</td>
            <td><a href="${request.route_path("asset_detail", asset_type=asset.discriminator, asset_id=asset.id)}">${asset}</a></td>
        </tr>
        %endfor
    </tbody>
</table>
