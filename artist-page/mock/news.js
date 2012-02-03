$(function() {
   $('#accordion dd').hide();
   $('#accordion dt a').click(function(){
       $('#accordion dd').slideUp();
       $(this).parent().next().slideDown();
       return false;
   });
});