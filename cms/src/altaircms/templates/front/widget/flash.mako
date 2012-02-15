## Flashウィジェットテンプレート
<script type="text/javascript">
$(document).ready(function(){
    var flashvars = {};
    var params = {};
    var attributes = {};

    var width = $('#id-widget-flash-${widget.id}').width();
    var height = $('#id-widget-flash-${widget.id}').height(); // @TODO: 高さ情報をどこから取得するか検討する

    swfobject.embedSWF(
        "${widget.url}",
        "id-widget-flash-${widget.id}",
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
<div id="id-widget-flash-${widget.id}"></div>
