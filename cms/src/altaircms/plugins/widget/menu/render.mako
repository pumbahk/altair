## menu widget output template
## 

<div class="menu-widget">
<ul class="menu">
  % for page in pages:
    <li ${'class="selected"' if page.id == thispage.id else ""|n}>
       <a href="${h.front.to_publish_page(request,page)}">${page.title}</a>
    </li>
  % endfor
</ul>
<div class="clear"/>
</div>
