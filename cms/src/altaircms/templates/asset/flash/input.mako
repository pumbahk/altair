<%inherit file='../../layout_2col.mako'/>
<%namespace name="fco" file="../../formcomponents.mako"/>

<h2>flash asset</h2>

<div class="row">
    <div class="span10">
        <ul class="breadcrumb">
            <li><a href="${request.route_path("asset_list")}">asset</a> <span class="divider">/</span></li>
            <li><a href="${request.route_path("asset_flash_list")}">flash</a> <span class="divider">/</span></li>
            <li><a href="${request.route_path("asset_flash_detail", asset_id=asset.id)}">${asset.filepath}</a></li>
            <li>${asset.filepath}</li>
        </ul>
    </div>
</div>

<div class="row">
    <%include file='../parts/flash.mako'/>
</div>

<div class="row">
  <h4>アセットの内容変更</h4>

  <div class="span6">
	<form action="${request.route_path("asset_flash_update", asset_id=asset.id)}" method="POST" enctype="multipart/form-data">
      ${fco.formfield(form, "filepath")}
      ${fco.formfield(form, "placeholder")}
      ${fco.formfield(form, "tags")}
      ${fco.formfield(form, "private_tags")}
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> Update</button>
    </form>
  </div>
</div>
