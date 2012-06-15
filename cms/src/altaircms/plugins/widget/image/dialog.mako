<%namespace file="../components.mako" name="co"/>

## N個ごとに区切られたitreratorを受け取り、divで区切って出力(scrollのため)
<%def name="render(assets)">
  % for g in assets:
  <div>
     % for image in g:
       <div class="item">
         <img pk="${image.id}" src="${h.asset.to_show_page(request,image)}" alt=""/>
         <p>title:${image.title} width:${image.width} height:${image.height} </p>
       </div>
     % endfor          
  </div>
  % endfor 
</%def>

<div class="title">
  <h1>画像(image)</h1>
</div>

<link rel="stylesheet" type="text/css" href="/plugins/static/css/widget/lib/image.css">
<!-- "previous page" action -->
<a class="prev browse left"></a>
<a class="next browse right"></a>
<div class="navi"></div>    

<!-- root element for scrollable -->
<div class="scrollable">   
   <!-- root element for the items -->
   <div class="items">
   ${render(assets)}
   </div>
</div>
<table class="table">
  <tbody>
    ${co.formfield(form, "href")}
  </tbody>
</table>
<button type="button" id="image_submit">登録</button>

