;(function($) {
	$.fn.tile = function(columns) {
		var tiles, max, c, h, last = this.length - 1, s;
		if(!columns) columns = this.length;
		this.each(function() {
			s = this.style;
			if(s.removeProperty) s.removeProperty("height");
			if(s.removeAttribute) s.removeAttribute("height");
		});
		return this.each(function(i) {
			c = i % columns;
			if(c == 0) tiles = [];
			tiles[c] = $(this);
			h = tiles[c].height();
			if(c == 0 || h > max) max = h;
			if(i == last || c == columns - 1)
				$.each(tiles, function() { this.height(max); });
		});
	};
})(jQuery);





// レスポンシヴ
$(function(){
    var minWidth = 450;
    if (minWidth <= $(this).width()) {
        $(".tile2").tile(2);
      $(window).load(function() {
        $(".tile2").tile(2);
      });
		}
    $(window).resize(function(){
        if (minWidth <= $(this).width()) {
        $(".tile2").tile(2);
        }
        else {
            $('.tile2,.tile4 li').removeAttr('style');
        }
    });
});




// PCのみ 
/* 
$(function() {
　　$(".tile2").tile(2);
　　$(".tile4 li").tile(4);
});
*/