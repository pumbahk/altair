## N個ごとに区切られたitreratorを受け取り、divで区切って出力(imageのため)
<%def name="render(image_assets)">
  % for g in image_assets:
  <div>
     % for image in g:
       ## <img pk="${image.id}" src="${image.filepath}" />
       <img pk="${image.id}" src="${request.route_url('asset_edit', asset_id=image.id)}?raw=t" alt=""/>
     % endfor          
  </div>
  % endfor 
</%def>

<link rel="stylesheet" type="text/css" href="/plugins/static/css/widget/lib/image.css">
<!-- "previous page" action -->
<a class="prev browse left"></a>
<a class="next browse right"></a>
<div class="navi"></div>    

<!-- root element for scrollable -->
<div class="scrollable">   
   <!-- root element for the items -->
   <div class="items">
   ${render(image_assets)}
   </div>
</div>
