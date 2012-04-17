<%inherit file='../../layout_2col.mako'/>
<%namespace name="fco" file="../../formcomponents.mako"/>

<h2>movie asset</h2>

<div class="row">
  <ul class="nav nav-tabs">
	<li><a href="${request.route_path("asset_list")}">all</a></li>
    <li><a href="${request.route_path("asset_image_list")}">image</a></li>
  	<li class="active"><a href="${request.route_path("asset_movie_list")}">movie</a></li>
   	<li><a href="${request.route_path("asset_flash_list")}">flash</a></li>
  </ul>
</div>

<div class="row">
  <h4>アセットの追加</h4>

  <div class="span6">
	<form action="${request.route_path("asset_movie_create")}" method="POST" enctype="multipart/form-data">
      ${fco.formfield(form, "filepath")}
      ${fco.formfield(form, "placeholder")}
      ${fco.formfield(form, "tags")}
      ${fco.formfield(form, "private_tags")}
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
                <td><a href="${request.route_path("asset_movie_detail", asset_id=asset.id)}">${asset}</a></td>
            </tr>
            %endfor
    </tbody>
</table>
