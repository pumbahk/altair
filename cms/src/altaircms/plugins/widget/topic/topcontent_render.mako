## topic widget output template
## 

## todo:画像を表示
## todo:カウントダウン表示
##
<div class="topcontent-list">
  %for topcontent in topcontents:
  <div class="topcontent" title="<h2>${topcontent.title}(${h.base.jdate(topcontent.publish_open_on)})</h2><p>${topcontent.text or ""|n}</p>">
    ${topcontent.title}(${h.base.jdate(topcontent.publish_open_on)})
  </div>
  %endfor
</div>
