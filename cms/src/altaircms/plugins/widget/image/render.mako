## 画像ウィジェット
## @TODO: height, widthといった属性は必要か?
<div class="image-widget">
    ## <img src="${widget.asset.filepath}"/>
    <img src="${request.route_url('asset_edit', asset_id=widget.asset.id)}?raw=t" alt="${widget.asset.alt}"/>
</div>
