## 画像ウィジェット
## @TODO: height, widthといった属性は必要か?
<%def name="render(request,widget)">
%if widget.href:
<a href="${widget.href}">
  <img 
	 ${'width="%d"' % widget.width  if widget.width else ""|n}
	 ${'height="%d"' % widget.height  if widget.height else ""|n}
	 src="${h.asset.to_show_page(request,widget.asset)}" alt="${widget.alt}"/>
</a>
%else:
  <img src="${h.asset.to_show_page(request,widget.asset)}" alt="${widget.alt}"/>
%endif
</%def>
%if widget.nowrap:
    ${render(request, widget)}
%else:
<div class="image-widget">
    ${render(request, widget)}
</div>
%endif
