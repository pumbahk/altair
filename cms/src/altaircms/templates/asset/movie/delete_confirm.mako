<%inherit file='../../layout_2col.mako'/>
<%namespace name="co" file="../components.mako"/>

<div class="row">
    <div class="span10">
        <ul class="breadcrumb">
            <li><a href="${request.route_path("asset_list")}">アセット</a> <span class="divider">/</span></li>
            <li>${asset.filepath}</li>
        </ul>
    </div>
</div>

<div class="alert alsert-error">
  このアセットを消します。良いですか？
</div>

<div class="row">
   ${co.movie_asset_describe(request, asset)}
</div>

<div class="row">
  <form action="${request.route_path("asset_movie_delete",asset_id=asset.id)}" method="post">
    <button class="btn btn-danger" type="submit"><i class="icon-trash"> </i> Delete</button>
  </form>
</div>
