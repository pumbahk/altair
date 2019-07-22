

$(function(){
  $('a[href^="#"]').click(function() {
      var speed = 400;
      var href= $(this).attr("href");
      var target = $(href == "#" || href == "" ? 'html' : href);
      var position = target.offset().top;
      $('body,html').animate({scrollTop:position}, speed, 'swing');
      return false;
   });
});



$(function(){
  $('.HamburgerWrap').click(function() {
    $('.smpNav').toggleClass("on");
  });
  $('.searchSmpwrap').click(function() {
    $('#search').addClass("searchOn");
  });
  $('.smpClose').click(function() {
    $('#search').removeClass("searchOn");
  });
  $('.topSlider_more').click(function() {
    $(this).prev().toggleClass("swon")
    $(this).toggleClass("swon")
  });
  var times = 700;
  $('.arrow').animate({opacity: 0}, times).animate({opacity: 1}, times).animate({opacity: 0}, times).animate({opacity: 1}, times).animate({opacity: 0}, times).queue(function(){
    $(this).addClass('arrowBox');
  });
});

$(function(){
  var scroll_a = 0;
  var scroll_n = 0;
$(window).scroll(function() {
  scroll_a = $(this).scrollTop();
  console.log(scroll_a)
  if (scroll_a<scroll_n) {
    $('header').addClass('next');
    $('header').removeClass('pre');
    $('.smpNav').addClass('next');
    $('.smpNav').removeClass('pre');
    $('.smpNav').removeClass('on');
    console.log("a")
  } else if(scroll_a<= 150 ) {
    $('header').addClass('next');
    $('header').removeClass('pre');
    $('.smpNav').addClass('next');
    $('.smpNav').removeClass('pre');
    $('.smpNav').removeClass('on');
    console.log("c")
  } else if(scroll_a>scroll_n) {
    $('header').addClass('pre');
    $('header').removeClass('next');
    $('.smpNav').addClass('pre');
    $('.smpNav').removeClass('next');
    $('.smpNav').removeClass('on');
    console.log("b")

  }
  scroll_n = scroll_a;
});
});