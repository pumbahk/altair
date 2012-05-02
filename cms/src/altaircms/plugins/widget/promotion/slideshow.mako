<html>
  <head>
  <style type="text/css">
	img {
	  margin: 0;
	  padding: 0;
	}
	.thumbnail img {
	  width: 80px;
	  height: 60px;
	}
	.mainImage img {
	  width: 425px;
	}
	.mainImageMessage {
	  background-color: #000;
	  color: #fff;
	}
	#slideShow {
	  width: 742px;
	}
	#slideShowLeft {
	  width: 425px;
	  float: left;
	}
	#slideShowRight {
	  width: 280px;
	  float: left;
	}
	#slideShowMiniRight {
	  width: 80px;
	  float: left;
	}
	#slideshowMiniRight img{
	  margin: 10px;
	}
  </style>
  <script type="text/javascript">
	// todo: refactoring
	var i = 0;
	var pu_candidates = [1,2,3,4,5]; //todo modify it;
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
			$(".mainImage img").attr("src", data.src);
			$(".mainImagemessage").text(data.message);
	      });
        }, 5000);
	});
  </script>
  </head>
  <body>
	<div id="slideShow">
	  <div id="slideShowLeft">
		<div class="mainImage">
		  ${show_image(info.main)|n}
		</div>
		<div class="mainImagemessage">
		  ${info.message}
		</div>
	  </div>
	  <div id="slideShowRight">
		<div class="thumbnail">
		 ${u"".join(show_image(thumb) for thumb in info.thumbnails)|n}
		</div>
	  </div>
	</div>
  </body>
</html>
