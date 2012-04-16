<%inherit file='../../layout_2col.mako'/>
<%namespace name="fco" file="../../formcomponents.mako"/>

<h2>image asset</h2>

<div class="row">
    <div class="span10">
        <ul class="breadcrumb">
            <li><a href="${request.route_path("asset_list")}">asset</a> <span class="divider">/</span></li>
            <li><a href="${request.route_path("asset_image_list")}">image</a> <span class="divider">/</span></li>
            <li><a href="${request.route_path("asset_image_detail", asset_id=asset.id)}">${asset.filepath}</a></li>
            <li>${asset.filepath}</li>
        </ul>
    </div>
</div>

<div class="row">
    <%include file='../parts/image.mako'/>
</div>

<div class="row">
  <h4>アセットの内容変更</h4>

  <div class="span6">
	<form action="${request.route_path("asset_image_update", asset_id=asset.id)}" method="POST" enctype="multipart/form-data">
      ${fco.formfield(form, "filepath")}
      ${fco.formfield(form, "tags")}
      ${fco.formfield(form, "private_tags")}
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> Update</button>
    </form>
  </div>
</div>
