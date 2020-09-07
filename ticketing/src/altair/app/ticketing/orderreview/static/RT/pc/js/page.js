//=========================================
// PC/SP 別設定
//=========================================


$(function(){
var windowWidth = $(window).width();
var windowSm = 768;
if (windowWidth <= windowSm) {
	//横幅768px以下のとき（つまりスマホ時）に行う処理を書く
	/********************** pc script start ******************************/
	
	
	
	/*********************** pc script end ******************************/
} else {
	//横幅768px超のとき（タブレット、PC）に行う処理を書く
	/********************** sp script start ******************************/
	
	
	
	/*********************** sp script end ******************************/
}
});



//=========================================
// PC/SP 共通
//=========================================

$(function(){
	var ua = navigator.userAgent.toLowerCase();
	var isiOS = (ua.indexOf('iphone') > -1) || (ua.indexOf('ipad') > -1);
	if(isiOS) {
		var viewport = document.querySelector('meta[name="viewport"]');
		if(viewport) {
			var viewportContent = viewport.getAttribute('content');
			viewport.setAttribute('content', viewportContent + ', user-scalable=no');
		}
	}
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

$(function(){
  var $thread = document.querySelector('#live-area-inner')
  var $thbtn = document.querySelector('.thread-btn')
  if(!($('#live-area-inner-thread').length)){
    $thread.classList.toggle('no-thread');
    $thbtn.classList.toggle('no-thread');
  }
});

//user
$(function(){
  if (navigator.userAgent.indexOf('iPhone') > 0) {
    let body = document.getElementsByTagName('body')[0];
    body.classList.add('iphone');
  }
});
$(function(){
  if ( navigator.userAgent.indexOf('Android') > 0 ) {
    let body = document.getElementsByTagName('body')[0];
    body.classList.add('android');
  }
});

//thread on/off
$(function(){
  var $target = document.querySelector('.target')
  var $button = document.querySelector('.button')
  var $live = document.querySelector('#live-area-inner')
  $button.addEventListener('click', function() {
    $target.classList.toggle('is-hidden');
    $live.classList.toggle('one-live');
    $button.classList.toggle('off')
  })
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







