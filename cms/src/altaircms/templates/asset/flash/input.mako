<%inherit file='../../layout_2col.mako'/>
<%namespace name="fco" file="../../formcomponents.mako"/>
<%namespace name="co" file="../components.mako"/>

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
    ${co.flash_asset_describe(request, asset)}
</div>

<div class="row">
  <h4>アセットの内容変更</h4>

  <div class="span6">
	<form action="${request.route_path("asset_flash_update", asset_id=asset.id)}" method="POST" enctype="multipart/form-data">
      ${fco.form_as_table_strict(form, ["filepath","title","placeholder","tags","private_tags"])}
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> Update</button>
    </form>
  </div>
</div>
