## movie widget dialog
##  view function is views.MovieWidgetView.dialog
##
## N個ごとに区切られたitreratorを受け取り、divで区切って出力(scrollのため)
<%def name="render(assets)">
  % for g in assets:
  <div>
     % for movie in g:
       <img pk="${movie.id}" src="${h.asset.to_show_page(request,movie,filepath="imagepath")}" alt=""/>
     % endfor          
  </div>
  % endfor 
</%def>

<div class="title">
  <h1>動画(movie)</h1>
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
