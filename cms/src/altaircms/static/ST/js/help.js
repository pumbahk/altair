$(function(){
  $('.help_list dt p').click(function() {
    $(this).parent().parent().find("dd").slideToggle();
    $('.help_list').toggleClass("on");
  });
});


