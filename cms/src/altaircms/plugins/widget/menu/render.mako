## menu widget output template
## 

<div class="menu-widget">
<ul class="menu">
  % for item in items:
    ## buggy
    <li ${'class="selected"' if cur_path == item["link"] else ""|n}>
       <a href="${item["link"]}">${item["label"]}</a>
    </li>
  % endfor
</ul>
<div class="clear"/>
</div>
