## menu widget output template
## 

<div class="menu-widget">
<ul class="menu">
  % for item in items:
    <li ${'class="selected"' if thispage.url in item["link"] else ""|n}>
       <a href="${item["link"]}">${item["label"]}</a>
    </li>
  % endfor
</ul>
<div class="clear"/>
</div>
