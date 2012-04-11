<%inherit file='base.mako'/>

<div class="alert alsert-error">
  このアセットを消します。良いですか？
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
  <form action="${request.route_path("asset_delete",asset_id=asset.id)}" method="post">
    <button class="btn btn-danger" type="submit"><i class="icon-trash"> </i> Delete</button>
  </form>
</div>
