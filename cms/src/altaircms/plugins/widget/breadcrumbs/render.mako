## breadcrumbs widget output template
## 

<div class="breadcrumbs">
	%for n in reversed(page.pageset.ancestors):
	  <a class="breadcrumb" href="${h.front.to_publish_page_from_pageset(request,n) }">${n.name}</a> &raquo;
    %endfor
    <span class="breadcrumb">${page.name}</span>
</div>
