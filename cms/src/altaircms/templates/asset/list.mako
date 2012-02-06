<%inherit file='../layout.mako'/>

<h1>アセットの追加</h1>
<ul>
<li><a href="${request.route_url('asset_form', asset_type="image")}">画像を追加する</a></li>
<li><a href="${request.route_url('asset_form', asset_type="movie")}">動画を追加する</a></li>
<li><a href="${request.route_url('asset_form', asset_type="flash")}">Flashを追加する</a></li>
</ul>

<ul>
%for asset in assets:
            <li>${asset}}</li>
%endfor
</ul>