## 画像ウィジェット
## @TODO: height, widthといった属性は必要か?
<div class="image-widget">
    ## <img src="${widget.asset.filepath}"/>
    <img src="${h.asset.to_show_page(request,widget.asset)}" alt="${widget.asset.alt}"/>
</div>
