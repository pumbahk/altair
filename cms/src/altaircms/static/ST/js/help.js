$(function(){
  $('.help_list dt p').click(function() {
    $('.help_list dd').slideToggle();
    $('.help_list').toggleClass("on");
  });
});


