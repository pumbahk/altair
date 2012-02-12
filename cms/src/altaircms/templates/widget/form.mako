<%inherit file='../layout.mako'/>
<%block name='js'>
    <script type="text/javascript" src="/static/deform/js/jquery.form.js"></script>
    <script type="text/javascript" src="/static/deform/js/jquery.maskedinput-1.2.2.min.js"></script>
    <script type="text/javascript" src="/static/deform/js/deform.js"></script>
</%block>
<%block name='style'>
    <link rel="stylesheet" href="/static/deform/css/form.css" type="text/css" />
</%block>
<%block name='jquery'>deform.load();</%block>

<h1>ウィジェット追加 / 編集</h1>

<a href="${request.route_url('widget_list')}">ウィジェット一覧</a>

%if widget:
<hr/>

    %if widget.type == 'flash_widget':
        <%include file='parts/flash.mako'/>
    %elif widget.type == 'movie_widget':
        <%include file='parts/movie.mako'/>
    %elif widget.type == 'image_widget':
        <%include file='parts/image.mako'/>
    %endif
    ${widget}
%endif

<hr/>

<div id="widget-form">
    ${form}
</div>

%if widget:
<form action="${request.route_url('widget_delete', widget_id=widget.id)}" method="post">
  <input type="hidden" name="_method" value="delete">
  <button type="submit">削除</button>
</form>
%endif