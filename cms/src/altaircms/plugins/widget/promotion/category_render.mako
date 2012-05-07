## promotion widget output template
## 

<div class="promotion-widget">
  <div id="categorySlideShow">
    <div id="slideShowLeft">
      <div class="mainImage">
        ${show_image(info.main,info.main_link)|n}
      </div>
      <div class="mainImageMessage">
        ${info.message}
      </div>
    </div>
    <div id="slideShowRight">
      <div class="thumbnail">
       ${u"".join(show_image(thumb,link) for thumb,link in zip(info.thumbnails, info.links))|n}
      </div>
    </div>
  </div>
</div>

  <script type="text/javascript">
    var i = 0;
    var pu_candidates = ${info.unit_candidates};
    var interval_time = ${info.interval_time}
    pu_candidates.next_id = function(){
      ++i;
      if(i>=this.length){
        i = 0;
      }
      return this[i];
    }

    $(function(){
      setInterval(function(){
        var params = {promotion_unit_id: pu_candidates.next_id()};
        $.getJSON("/api/promotion/mainimage", params).done(
          function(data){
            var img = $(".mainImage img");
            img.attr("src", data.src);
            img.parent("a").attr("href", data.link)
            $(".mainImageMessage").text(data.message);
          });
        }, interval_time);
    });
  </script>
