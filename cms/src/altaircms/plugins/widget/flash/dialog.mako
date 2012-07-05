## flash widget dialog
##  view function is views.FlashWidgetView.dialog
##
<%def name="render(assets)">
  % for g in assets:
  <div>
     % for flash in g:
       <img pk="${flash.id}" src="${h.asset.to_show_page(request,flash,filepath=flash.imagepath)}" alt=""/>
     % endfor          
  </div>
  % endfor 
</%def>

<div class="title">
  <h1>flash</h1>
</div>

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
