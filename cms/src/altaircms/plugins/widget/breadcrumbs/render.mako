## breadcrumbs widget output template
## 

<div class="breadcrumbs">
	%for n in reversed(page.ancestors):
	  <a class="breadcrumb" href="${h.front.to_publish_page(request,n) }">${n.title}</a> &raquo;
    %endfor
    <span class="breadcrumb">${page.title}</span>
</div>
