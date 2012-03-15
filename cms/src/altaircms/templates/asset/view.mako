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
    <form action="${request.route_path("asset_edit", asset_id=asset.id)}" method="post">
        <input type="hidden" name="_method" value="delete"/>
        <button class="span4 btn" type="submit"><i class="icon-trash"> </i> このアセットを削除</button>
    </form>
</div>
