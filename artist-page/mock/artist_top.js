<script type ="text/javascript">
$(function(){
     $(".focus").focus(function(){
          if(this.value == "キーワードを入力"){
               $(this).val("").css("color","#f39");
          }
     });
     $(".focus").blur(function(){
          if(this.value == ""){
               $(this).val("キーワードを入力").css("color","#969696");
          }
     });
});
</script>
