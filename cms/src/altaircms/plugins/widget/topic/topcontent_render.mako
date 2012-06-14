## topic widget output template
## 

## todo:画像を表示
## todo:カウントダウン表示
##
<div class="topcontent-list">
  %for topcontent in topcontents:
  <div class="topcontent" title="<h2>${topcontent.title}(${h.base.jdate(topcontent.publish_open_on)})</h2><p>${topcontent.text or ""|n}</p>">
    ${topcontent.title}(${h.base.jdate(topcontent.publish_open_on)})
    <a href="${h.link.get_link_from_topcontent(request,topcontent)}"><img src="${h.asset.to_show_page(request,topcontent.image_asset)}"/>
  </div>
  %endfor
</div>
