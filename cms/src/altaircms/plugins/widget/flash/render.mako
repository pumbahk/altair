## flash widget output template
## 

## Flashウィジェットテンプレート
## todo remove it
<script type="text/javascript" src="/fanstatic/jquery/jquery.js"></script> 

<script type="text/javascript" src="/static/swfobject.js"></script>
<script type="text/javascript">
$(document).ready(function(){
    var flashvars = {};
    var params = {};
    var attributes = {};

    var width = $('#asset').width();
    var height = $('#asset').height(); // @TODO: 高さ情報をどこから取得するか検討する

    swfobject.embedSWF(
        "${request.route_url('asset_view', asset_id=asset.id)}?raw=t",
        "asset",
        width,
        "480",
        "9.0.0",
        "/static/expressInstall.swf",
        flashvars,
        params,
        attributes
    );
})
</script>
<div id="asset"></div>
