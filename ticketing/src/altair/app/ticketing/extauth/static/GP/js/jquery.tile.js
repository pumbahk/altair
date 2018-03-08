(function($) {
  $.fn.tile = function(columns) {
    var tiles, $tile, max, c, h, remove, s = document.body.style, a = ["height"],
      last = this.length - 1;
    if(!columns) columns = this.length;
    remove = s.removeProperty ? s.removeProperty : s.removeAttribute;
    return this.each(function() {
      remove.apply(this.style, a);
    }).each(function(i) {
      c = i % columns;
      if(c == 0) tiles = [];
      $tile = tiles[c] = $(this);
      h = ($tile.css("box-sizing") == "border-box") ? $tile.outerHeight() : $tile.innerHeight();
      if(c == 0 || h > max) max = h;
      if(i == last || c == columns - 1) {
        $.each(tiles, function() { this.css("height", max); });
      }
    });
  };
})(jQuery);

/*if(!navigator.userAgent.match(/(iPhone|iPad|Android)/)){
}*/	
	
$(function(){
	var tabWidth = 479,
	pcWidth = 767;

	if(pcWidth <= window.innerWidth){
		  $(window).load(function() {
			$('.loginArea dl').tile(2);
		  });
	}else if (tabWidth <= window.innerWidth) {
	  $(window).load(function() {
		$('.loginArea dl').tile(1);
	  });
	}
	$(window).resize(function(){
		if(pcWidth <= window.innerWidth){
			$('.loginArea dl').tile(2);
		}else if (tabWidth <= window.innerWidth) {
			$('.loginArea dl').tile(1);
		}else {
			$('.loginArea dl').removeAttr('style');
		}
	});
});
