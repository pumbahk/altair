$(document).ready(function() {
	$(".nav dt").hover(function(){
		$(this).css("cursor","pointer"); 
	},function(){
		$(this).css("cursor","default"); 
		});
	$(".nav dd").css("display","none");
	$(".nav dt").click(function(){
		$(this).next().toggle();
		});
});

function intext(){
     document.getElementById("toukou_tsuika").innerHTML="<div class ='kobetsu'><img src='hito1.jpg' id ='toukou_img'>hito1 新しい投稿</div><div class ='kobetsu'><img src='hito1.jpg' id ='toukou_img'>hito1 新しい投稿</div><div class ='kobetsu'><img src='hito1.jpg' id ='toukou_img'>hito1 新しい投稿</div>";
   document.getElementById("saishinn_toukou").innerHTML="";
     
}  

function toukoutext(){
     document.getElementById("toukou_tsuika").innerHTML="<div class ='kobetsu'><img src='hito1.jpg'>hito1投稿した文書</div>";
      
}  
$(function() {
      $('input:checkbox').checkbox();
  });
  
$(function() {
        
		//vars
		var conveyor = $(".content-conveyor", $("#sliderContent")),
		item = $(".item", $("#sliderContent"));
		
		//set length of conveyor
		conveyor.css("width", item.length * parseInt(item.css("width")));
				
        //config
        var sliderOpts = {
		  max: (item.length * parseInt(item.css("width"))) - parseInt($(".viewer", $("#sliderContent")).css("width")),
          slide: function(e, ui) { 
            conveyor.css("left", "-" + ui.value + "px");
          }
        };

        //create slider
        $("#slider").slider(sliderOpts);
      });
    
function changeimg(number){
    if(number == "2"){
     document.getElementById("print_okikae").innerHTML="<img src='subprint_img2.jpg'>";
    }
    else if(number =="3"){
    document.getElementById("print_okikae").innerHTML="<img src='subprint_img3.jpg'>";
    }
    else if(number =="4"){
    document.getElementById("print_okikae").innerHTML="<img src='subprint_img4.jpg'>";
    }
    else{
    document.getElementById("print_okikae").innerHTML="<img src='subprint_img5.jpg'>";
    }
}  
