## 動画ウィジェット
## @TODO: height, widthといった属性は必要か？
<div>
    %if widget.asset.mimetype == 'video/quicktime':
        <embed src="${request.route_url("asset_edit", asset_id=widget.asset.id)}?raw=t"></embed>
    %elif widget.asset.mimetype == 'video/mp4':
        <embed type="video/quicktime" src="${request.route_url("asset_edit", asset_id=widget.asset.id)}?raw=t"></embed>
    %endif
</div>
