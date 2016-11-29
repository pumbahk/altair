$(function(){
  $("#toggle").click(function(){
    $(".nav-global ul").slideToggle();
    return false;
  });
  $(window).resize(function(){
    var win = $(window).width();
    var p = 789;
    if(win > p){
      $(".nav-global ul").show();
    } else {
      $(".nav-global ul").hide();
    }
  });
});