## movie widget output template
## 
<div class="movie-widget">
    %if widget.asset.mimetype == 'video/quicktime':
        <embed src="${h.asset.to_show_page(request,widget.asset)}"></embed>
    %elif widget.asset.mimetype == 'video/mp4':
        <embed type="video/quicktime" src="${h.asset.to_show_page(request,widget.asset)}"></embed>
    %endif
</div>
