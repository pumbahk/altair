## 動画ウィジェット
## @TODO: height, widthといった属性は必要か？
<div>
    %if widget.mimetype == 'video/quicktime':
        <embed src="${widget.url}"></embed>
    %elif widget.mimetype == 'video/mp4':
        <embed type="video/quicktime" src="${widget.url}"></embed>
    %endif
</div>
