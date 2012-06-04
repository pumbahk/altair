## flash widget output template
## fixme: default width or height
<div class="flash-widget"
     url="${h.asset.to_show_page(request, widget.asset)}"
     pk="${widget.asset.id}"
     width="${widget.asset.width or 480}"
     height="${widget.asset.height or 480}"
></div>
