<%inherit file='../layout.mako'/>

%if asset.type == 'flash_asset':
<%include file='parts/flash.mako'/>
%elif asset.type == 'movie_asset':
<%include file='parts/movie.mako'/>
%elif asset.type == 'image_asset':
<%include file='parts/image.mako'/>
%endif

<form action="${request.route_url('asset_edit', asset_id=asset.id)}" method="post">
  <input type="hidden" name="_method" value="delete">
  <button type="submit">削除</button>
</form>
