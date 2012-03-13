## topic widget output template
## 

<div class="topic" title="<h2>${topic.title}(${h.base.jdate(topic.publish_at)})</h2><p>${topic.text|n}</p>">
  ${topic.title}(${h.base.jdate(topic.publish_at)})
</div>
## jsも追加される。
## $(function(){ $(".topic").tooltip();})
##

## cssは.topicに対して指定する必要がある。

####  e.g. 
##  /* tooltip用のcss*/
##  .tooltip h2 {
##    background-color:#ee8;
##  }
##  .tooltip {
##    display:none;
##    background-color:#ffa;
##    border:1px solid #cc9;
##    padding:3px;
##    width: 600px;
##    font-size:13px;
##    -moz-box-shadow: 2px 2px 11px #666;
##    -webkit-box-shadow: 2px 2px 11px #666;
##  }
