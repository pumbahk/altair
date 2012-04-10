<%inherit file='../../layout_2col.mako'/>
<%namespace name="co" file="../components.mako"/>

<h2>動画アセット詳細</h2>
<div class="row">
    <div class="span10">
        <ul class="breadcrumb">
            <li><a href="${request.route_path("dashboard")}">Top</a> <span class="divider">/</span></li>
            <li><a href="${request.route_path("asset_list")}">Asset</a> <span class="divider">/</span></li>
            <li><a href="${request.route_path("asset_movie_list")}">movie</a> <span class="divider">/</span></li>
            <li>${asset.filepath}</li>
        </ul>
    </div>
</div>


<div class="row">
    ${co.movie_asset_describe(request, asset)}
</div>

<div class="row">
    <a class="btn btn-danger" href="${request.route_path("asset_movie_delete",asset_id=asset.id)}"><i class="icon-trash icon-white"></i> このアセットを削除</a>
</div>
