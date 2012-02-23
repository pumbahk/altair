<%inherit file='../layout_2col.mako'/>

<div class="row" style="margin-bottom: 9px">
<h4>アセットの追加</h4>
<div class="btn-group">
<a class="btn" href="${request.route_url('asset_form', asset_type="image")}">画像</a>
<a class="btn" href="${request.route_url('asset_form', asset_type="movie")}">動画</a>
<a class="btn" href="${request.route_url('asset_form', asset_type="flash")}">Flash</a>
</div>
</div>

<div class="row">
<h4>登録済みのアセット一覧</h4>
<ul>
%for asset in assets:
            <li><a href="${request.route_url("asset_view", asset_id=asset.id)}">${asset}</a></li>
%endfor
</ul>
</div>
