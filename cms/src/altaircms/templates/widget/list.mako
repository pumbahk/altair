<%inherit file='../layout.mako'/>

<h1>ウィジェット</h1>
<ul>
<li><a href="${request.route_url("widget_add", widget_type='text')}">テキストウィジェット追加</a></li>
<li><a href="${request.route_url("widget_add", widget_type='image')}">画像ウィジェット追加</a></li>
<li><a href="${request.route_url("widget_add", widget_type='movie')}">動画ウィジェット追加</a></li>
<li><a href="${request.route_url("widget_add", widget_type='flash')}">Flashウィジェット追加</a></li>
</ul>

<h2>登録済みのウィジェット一覧</h2>
<ul>
%for widget in widgets:
    <li><a href="${request.route_url("widget", widget_id=widget.id)}">${widget}</a></li>
%endfor
</ul>
