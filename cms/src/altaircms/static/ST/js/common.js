

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
});

