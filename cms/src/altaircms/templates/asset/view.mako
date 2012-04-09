<%inherit file='base.mako'/>

<div class="row">
%if asset.type == 'flash':
<%include file='parts/flash.mako'/>
%elif asset.type == 'movie':
<%include file='parts/movie.mako'/>
%elif asset.type == 'image':
<%include file='parts/image.mako'/>
%endif
</div>

<div class="row">
    <a class="btn btn-danger" href="${request.route_path("asset_delete",asset_id=asset.id)}"><i class="icon-trash icon-white"></i> このアセットを削除</a>
</div>
