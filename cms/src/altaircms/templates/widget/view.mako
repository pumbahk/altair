<%inherit file='../layout.mako'/>

%if widget.type == 'flash_widget':
<%include file='parts/flash.mako'/>
%elif widget.type == 'movie_widget':
<%include file='parts/movie.mako'/>
%elif widget.type == 'image_widget':
<%include file='parts/image.mako'/>
%endif

<form action="${request.route_url('widget', widget_id=widget.id)}" method="post">
  <input type="hidden" name="_method" value="delete">
  <button type="submit">削除</button>
</form>
