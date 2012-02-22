<%inherit file='../layout.mako'/>

%if asset.type == 'flash_asset':
<%include file='parts/flash.mako'/>
%elif asset.type == 'movie_asset':
<%include file='parts/movie.mako'/>
%elif asset.type == 'image_asset':
<%include file='parts/image.mako'/>
%endif

<form action="${h.asset.to_show_page(request,asset)}" method="post">
  <input type="hidden" name="_method" value="delete">
  <button type="submit">削除</button>
</form>
