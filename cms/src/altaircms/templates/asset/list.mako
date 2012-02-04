<%inherit file='../layout.mako'/>

<a href="${request.route_url('asset_form', asset_type="image")}">アセットを追加する</a>
<ul>
%for asset in assets:
            <li>${asset}}</li>
%endfor
</ul>