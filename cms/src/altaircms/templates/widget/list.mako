<%inherit file='../layout.mako'/>

<h1>ウィジェット</h1>
<ul>
    <li><a href="${request.route_path("widget_add", widget_type='text')}">テキストウィジェット追加</a></li>
    <li><a href="${request.route_path("widget_add", widget_type='image')}">画像ウィジェット追加</a></li>
    <li><a href="${request.route_path("widget_add", widget_type='movie')}">動画ウィジェット追加</a></li>
    <li><a href="${request.route_path("widget_add", widget_type='flash')}">Flashウィジェット追加</a></li>
    <li><a href="${request.route_path("widget_add", widget_type='breadcrumbs')}">パンくずウィジェット追加</a></li>
    <li><a href="${request.route_path("widget_add", widget_type='menu')}">メニューウィジェット追加</a></li>
    <li><a href="${request.route_path("widget_add", widget_type='topic')}">トピックウィジェット追加</a></li>
    <li>購入履歴ウィジェット追加（ユーザオブジェクトから情報取得、描画を行えるため、事前定義不要）</li>
    <li>チケットリストウィジェット追加（イベントから情報取得、描画を行えるため、事前定義不要）</li>
    <li>席図ウィジェット追加（イベントから情報取得、描画を行えるため、事前定義不要）</li>
    <li>カウントダウンウィジェット追加（イベントから情報取得、描画を行えるため、事前定義不要）</li>
    <li>イベント詳細ウィジェット追加（イベントから情報取得、描画を行えるため、事前定義不要）</li>
    <li>イベント概要ウィジェット追加（イベントから情報取得、描画を行えるため、事前定義不要）</li>
    <li>カレンダウィジェット追加（イベントから情報取得、描画を行えるため、事前定義不要）</li>
</ul>

<h2>登録済みのウィジェット一覧</h2>
<ul>
%for widget in widgets:
    <li><a href="${request.route_path("widget", widget_id=widget.id)}">${widget}</a></li>
%endfor
</ul>
