//=========================================
// PC/SP 別設定
//=========================================


$(function(){
var windowWidth = $(window).width();
var windowSm = 640;
if (windowWidth <= windowSm) {
	//スマホ時に行う処理
	/********************** sp script start ******************************/
	
		$(function() {
		$('#tabMenu li').matchHeight();
		});
	
	/*********************** sp script end ******************************/
} else {
	//タブレット、PCに行う処理
	/********************** pc script start ******************************/
	
	/*********************** pc script end ******************************/
}
});


//=========================================
// PC/SP 共通
//=========================================

$(function() {
	$('.acordion_tree dt, .acordion_tree dd').matchHeight();
});

//スライダー
$(function() {
    $('.center-item').slick({
          infinite: true,
          dots:true,
          slidesToShow: 1,
          centerMode: true, //要素を中央寄せ
          centerPadding:'15%', //両サイドの見えている部分のサイズ
          autoplay:true, //自動再生
          responsive: [{
               breakpoint: 768,
               settings: {
                  centerMode: false,
               }
          }]
     });
});

//スムーズスクロール
$(function(){
	$('a[href^="#"]').click(function(){
		var speed = 500;
		var href= $(this).attr("href");
		var target = $(href == "#" || href == "" ? 'html' : href);
		var position = target.offset().top;
		$("html, body").animate({scrollTop:position}, speed, "swing");
		return false;
	});
});

//アコーディオン上
$(document).ready(function(){
	$('.acdTp').click(function() {
		$(this).prev().slideToggle(500);
	}).prev().hide();
});

//アコーディオン下
$(document).ready(function(){
	$('.acdBt').click(function() {
		$(this).next().slideToggle(500);
	}).next().hide();
});

//タブ（ボタンの記述順番と、コンテンツの記述順番で連動）
$(function() {
	$('#tabMenu li').click(function() {
		var index = $('#tabMenu li').index(this);
		$('#artistBox .tabCnt').css('display','none');
		$('#artistBox .tabCnt').eq(index).css('display','block');
		$('#tabMenu li').removeClass('tabSelect');
		$(this).addClass('tabSelect')
	});
});



//=========================================
// コードサンプル
//=========================================

//条件による実行処理その1
$(function(){
	if($('#sample').length){
		/////////////////////
		
		//ここに「#sample」が存在した場合の処理を記述
		
		/////////////////////
	}
});


//条件による実行処理その2
$(function(){
	if(!($('').length)){
		/////////////////////
		
		//ここに「#sample」が存在しなかった場合の処理を記述
		
		/////////////////////
	}
});


//ブラウザリサイズ時に自動リロード
//$(function(){
//	var timer = false;
//	$(window).resize(function() {
//	if (timer !== false) {
//	clearTimeout(timer);
//	}
//	timer = setTimeout(function() {
//	location.reload();
//	}, 200);
//	});
//});







