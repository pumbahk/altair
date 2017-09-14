

var windowWidth = $(window).width();
var windowSm = 768;
if (windowWidth <= windowSm) {
    //横幅640px以下のとき（つまりスマホ時）に行う処理を書く
} else {
    //横幅640px超のとき（タブレット、PC）に行う処理を書く
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
		
		$(function(){
			$('.customer-table th, .customer-table td').tile(2);
			$('.customer-table3 th, .customer-table3 td').tile(2);
			$('.customer-table4 th, .customer-table4 td').tile(2);
		});
}

/*-------------------------------------*/

$(document).ready(function(){
  $(".methodExplanation").hide();
  // show the info that is already clicked
  var clicked_item = $("input[id^='radio']").filter(':checked');
  $(clicked_item).parent().next().show();

  $("dt.settlement-list").on('click', function(e) {
    var clicked_radio = $(this).find("input[id^='radio']");
    var index = $("input[id^='radio']").index(clicked_radio);
    var vis_item = $(".methodExplanation:visible");
    // uncheck the radio and close the info block when it is clicked again
    if ($(clicked_radio).is(':checked') & $(this).next().is(':visible')) {
      e.preventDefault();
      $(clicked_radio).prop('checked', false);
      $(this).next().slideUp();
    } else {
      var do_shift = false;
      var shift = 0;
      // decide whether the position setting needs to include the height of previous info block
      if ($(vis_item).length === 1) {
        var vis_index =  $(".methodExplanation").index($(vis_item));
        // if the index of visible item is less than that of the clicked item.
        do_shift = vis_index < index;
      }

      // set the position to be shifted.
      if (do_shift) {
        var margin = +$(vis_item).css('margin-top').replace("px", "");
        margin += +$(vis_item).css('margin-bottom').replace("px", "");
        shift = $(vis_item).height() + margin;
      }
      $(".methodExplanation").slideUp();
      $(this).next().slideDown();
      $(clicked_radio).prop('checked', true);
      // shift the position to show the info properly
      $('html, body').animate({
        scrollTop: $(this).offset().top - shift
      });
    }
  });
});

/*-------------------------------------*/

/*
$(function(){
	var timer = false;
	$(window).resize(function() {
	if (timer !== false) {
	clearTimeout(timer);
	}
	timer = setTimeout(function() {
	location.reload();
	}, 200);
	});
});
*/

/*-------------------------------------*/

$(function() {
	$('#submit').attr('disabled', 'disabled');
	
	$('#ruleCheck').click(function() {
		if ($(this).prop('checked') == false) {
			$('#submit').attr('disabled', 'disabled');
		} else {
			$('#submit').removeAttr('disabled');
		}
	});
});

/*********************************

var windowWidth = $(window).width();
var windowSm = 768;
if (windowWidth <= windowSm) {
    //横幅640px以下のとき（つまりスマホ時）に行う処理を書く
} else {
    //横幅640px超のとき（タブレット、PC）に行う処理を書く
}

*********************************/
