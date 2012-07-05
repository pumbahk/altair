## flash widget output template
## fixme: default width or height
<div class="flash-widget"
     url="${h.asset.to_show_page(request, widget.asset)}"
     pk="${widget.asset.id}"
     width="${widget.asset.width or 480}"
     height="${widget.asset.height or 480}"
></div>
## this is not good
<script type="text/javascript" src="/static/swfobject.js"></script>
<script type="text/javascript">
$(function(){
    $(".flash-widget").each(function(i,e){
        var flashvars = {};
        var params = {};
        var attributes = {};

        var e = $(e);
        var width = e.attr("width");
        var height = e.attr("height");
        var url = e.attr("url");
        var uid = String(Math.random()); //slack-off
        e.attr("id", uid)
        swfobject.embedSWF(
            url,
            uid, 
            width,
            height, 
            "9.0.0",
            "/static/expressInstall.swf",
            flashvars,
            params,
            attributes
        );
    });
});
</script>
