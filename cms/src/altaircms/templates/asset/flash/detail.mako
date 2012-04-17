<%inherit file='../../layout_2col.mako'/>

<div class="row">
    <div class="span10">
        <ul class="breadcrumb">
            <li><a href="${request.route_path("asset_list")}">asset</a> <span class="divider">/</span></li>
            <li><a href="${request.route_path("asset_flash_list")}">flash</a> <span class="divider">/</span></li>
            <li>${asset.filepath}</li>
        </ul>
    </div>
</div>


<div class="row">
    <%include file='../parts/flash.mako'/>
</div>

<div class="row">
    <a class="btn btn-primary" href="${request.route_path("asset_flash_input",asset_id=asset.id)}"><i class="icon-cog icon-white"></i> このアセットを変更</a>
    <a class="btn btn-danger" href="${request.route_path("asset_flash_delete",asset_id=asset.id)}"><i class="icon-trash icon-white"></i> このアセットを削除</a>
</div>
