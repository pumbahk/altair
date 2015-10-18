$(document).on('click', '#modal-close, #modal-overlay', function() {
  $("#modal-close, #modal-overlay").off("click");
  $("#modal-overlay").remove();
  $("#modal-content").css("display", "none");
});

$(document).on('click', '.coupon_button', function() {
  var next_url = $(this).attr("next_url");

  $(this).blur();
  //現在のモーダルウィンドウを削除して新しく起動する
  if($("#modal-overlay")[0]) $("#modal-overlay").remove();

  $("body").append('<div id="modal-overlay"></div>');
  $("#modal-overlay").fadeIn("slow");
  $("#modal-content").fadeIn("slow");

  // couponを使用するurl設定
  $('#coupon_form').attr("action", next_url);

  centeringModalSyncer();
});

function centeringModalSyncer(){
	var w = $(window).width();
	var h = $(window).height();
	var cw = $("#modal-content").outerWidth({margin:true});
	var ch = $("#modal-content").outerHeight({margin:true});
	var pxleft = ((w - cw)/2);
	var pxtop = ((h - ch)/2);
	$("#modal-content").css({"left": pxleft + "px"});
	$("#modal-content").css({"top": pxtop + "px"});
}
