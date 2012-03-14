<%inherit file='../layout.mako'/>

<div class="row">
    <div class="span12">
        <ul class="breadcrumb">
            <li><a href="${request.route_url("asset_list")}">アセット</a> <span class="divider">/</span></li>
            <li>${asset.filepath}</li>
        </ul>
    </div>
</div>

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
    <form action="${request.route_url("asset_edit", asset_id=asset.id)}" method="post">
        <input type="hidden" name="_method" value="delete"/>
        <button class="span4 offset4 btn" type="submit">このアセットを削除</button>
    </form>
</div>