$(function(){
    var ua = navigator.userAgent;
    if((ua.indexOf('iPhone') > 0) || ua.indexOf('iPod') > 0 || (ua.indexOf('Android') > 0 && ua.indexOf('Mobile') > 0)){
        $('head').prepend('<meta name="viewport" content="width=device-width,initial-scale=1">');
    } else {
        $('head').prepend('<meta name="viewport" content="width=1200">');
    }
});

$(function(){
  document.oncontextmenu = function () {return false;}
});

jQuery('.tkmt').click(function() {
  location.href = jQuery(this).attr('data-url');
});

new function(){
	//EXEC MouseOver Change img
	$(function(){
		$('a img').hover(function(){
			$(this).attr('src', $(this).attr('src').replace('_off.', '_on.'));
		}, function(){
			if (!$(this).hasClass('currentPage')) {
				$(this).attr('src', $(this).attr('src').replace('_on.', '_off.'));
			}
		});
	});
}


$(function() {
  function embedYouTube(){
    var youtube = document.getElementsByClassName('youtube');
    for(var i=0;i<youtube.length;i++){
      youtube[i].addEventListener('click',function(){
        video = '<iframe src="'+ this.getAttribute('data-video') +'" frameborder="0" width="100%" height="100%" style="position: absolute; top: 0; left: 0;"></iframe>';
        this.outerHTML = video;
      });
    }
  }
  embedYouTube();
});


$(function() {
  $('#news .news_box > li').matchHeight();
  $('#news .news_box h3').matchHeight();
  $('#news .news_box .news_txt').matchHeight();
  $('#news .news_box .news_link').matchHeight();
  $('#artist .artist_box > li').matchHeight();
});

$(function(){
  var headerHight = 100; //ヘッダの高さ  
  $('a[href^="#"]').click(function() {
      var speed = 400;
      var href= $(this).attr("href");
      var target = $(href == "#" || href == "" ? 'html' : href);
      var position = target.offset().top-headerHight;
      $('body,html').animate({scrollTop:position}, speed, 'swing');
      return false;
   });
});

//アコーディオン
$('.btn-toggle').on('click',function(e){
  e.preventDefault();

  $(this).next().slideToggle('fast');
  var checkIcon = $(this).find('.fa-plus-circle');
  if( checkIcon.size() ){
    checkIcon.toggleClass('.fa-minus-circle');
  }
});


$(function() {
  $('.slider').slick({
    autoplay: true,
    autoplaySpeed: 3500,
    arrows: false,
    cssEase: 'linear',
    dots: false,
		centerMode: true,
		centerPadding: 0,
    fade: true,
  });
});


jQuery(function($) {
  
var nav    = $('#maintop #fixedBox'),
    offset = nav.offset();
  
$(window).scroll(function () {
  if($(window).scrollTop() > offset.top) {
    nav.addClass('fixed');
  } else {
    nav.removeClass('fixed');
  }
});
  
});


$(function(){
  $('.smpnav_btn').click(function(){
      $('#smpwrap').toggleClass('on');
      $('#smpnav_btn').toggleClass('on');
      console.log("0")
  });

  $('#smpwrap a').click(function(){
      $('#smpwrap').removeClass('on');
      $('#smpnav_btn').removeClass('on'); 
    });

});