<%inherit file='../layout_2col.mako'/>

<h4>アセットの追加</h4>
<ul class="nav nav-pills">
<li><a href="${request.route_path('asset_form', asset_type="image")}">画像を追加する</a></li>
<li><a href="${request.route_path('asset_form', asset_type="movie")}">動画を追加する</a></li>
<li><a href="${request.route_path('asset_form', asset_type="flash")}">Flashを追加する</a></li>
</ul>

<h4>登録済みのアセット一覧</h4>
<table class="table table-striped">
    <tbody>
            %for asset in assets:
            <tr>
                <td>${asset.created_at}</td>
                <td>${asset.discriminator}</td>
                <td><a href="${request.route_path("asset_view", asset_id=asset.id)}">${asset}</a></td>
            </tr>
            %endfor
    </tbody>
</table>
