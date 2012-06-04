## promotion widget output template
## 

<div class="promotion-widget">
  <div id="subkindSlideShow">
    <div id="slideShowLeft">
      <div class="mainImage">
        ${show_image(info.main,info.main_link)|n}
      </div>
      <div class="mainImageMessage">
        ${info.message}
      </div>
    </div>
    <div id="slideShowRight">
      <div class="subkindThumbnail">
      %for thumb, link, message in zip(info.thumbnails, info.links, info.messages):
		<div class="slideBox">
		  <div class="slideBoxLeft">
            ${show_image(thumb, link)|n}
		  </div>
		  <div class="slideBoxRight">
			${message}
		  </div>
		  <div class="clear"></div>
		</div>
      %endfor
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
