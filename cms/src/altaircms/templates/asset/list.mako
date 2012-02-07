<%inherit file='../layout.mako'/>

<h1>アセットの追加</h1>
<ul>
<li><a href="${request.route_url('asset_form', asset_type="image")}">画像を追加する</a></li>
<li><a href="${request.route_url('asset_form', asset_type="movie")}">動画を追加する</a></li>
<li><a href="${request.route_url('asset_form', asset_type="flash")}">Flashを追加する</a></li>
</ul>

<h2>登録済みのアセット一覧</h2>
<ul>
%for asset in assets:
            <li><a href="${request.route_url("asset_view", asset_id=asset.id)}">${asset}</a></li>
%endfor
</ul>