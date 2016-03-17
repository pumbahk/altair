$(document).on('click', '#modal-close, #modal-overlay', function() {
  $("#modal-close, #modal-overlay").off("click");
  $("#modal-overlay").remove();
  $("#modal-content").css("display", "none");
  $("#alert-modal-content").css("display", "none");
});

function check_can_use_coupon(check_url){
  return $.ajax({
    type: 'GET',
    url: check_url
  })
}

$(document).on('click', '.coupon_button', function() {
  var next_url = $(this).attr("next_url");
  var check_url = $(this).attr("check_url");


  check_can_use_coupon(check_url).done(function(result) {
    if (result == true) {
      console.log("coupon is not used");
      $(this).blur();
      //現在のモーダルウィンドウを削除して新しく起動する
      if($("#modal-overlay")[0]) $("#modal-overlay").remove();

      $("body").append('<div id="modal-overlay"></div>');
      $("#modal-overlay").fadeIn("slow");
      $("#modal-content").fadeIn("slow");

      // couponを使用するurl設定
      $('#coupon_form').attr("action", next_url);

      centeringModalSyncer($("#modal-content"));
    } else {
      console.log("coupon is used");
      $(this).blur();
      //現在のモーダルウィンドウを削除して新しく起動する
      if($("#modal-overlay")[0]) $("#modal-overlay").remove();

      $("body").append('<div id="modal-overlay"></div>');
      $("#modal-overlay").fadeIn("slow");
      $("#alert-modal-content").fadeIn("slow");

      centeringModalSyncer($("#alert-modal-content"));
    }
  }).fail(function(result) {
  });
});

function centeringModalSyncer(content){
	var w = $(window).width();
	var h = $(window).height();
	var cw = content.outerWidth({margin:true});
	var ch = content.outerHeight({margin:true});
	var pxleft = ((w - cw)/2);
	var pxtop = ((h - ch)/2);
	content.css({"left": pxleft + "px"});
	content.css({"top": pxtop + "px"});
}
