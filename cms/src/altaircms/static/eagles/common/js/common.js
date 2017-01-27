// ============================================================
// ATTENTION & COMMON RULE!!
// 関数を実装のみ（処理の実行は下部で実行する）
// 関数名には振る舞いを表す英語プラスFuncを付ける
// ============================================================


// レスポンシブ判定 & デバイス判定関数（PC,SP共通処理）
// タブレットはiPad のみ判定しているが、別途判定が必要な場合はUAをclass名を追加する
//-------------------------------------------------------------

// グローバル変数
var desktopFlg,smartphoneFlg,ipadFlg;
var winWidth = window.innerWidth;
var ua = navigator.userAgent;
var breakPoint = 767; 
var y = window.pageYOffset;
var iframeHeight = 0;
function checkDeviceAndWidthFunc(){

  // iPad 判定
  if(ua.indexOf('iPad') > 0){
      ipad = true;
      document.getElementsByTagName("body")[0].setAttribute("class","tablet");
  }
  // PC or SP
  if (winWidth <= breakPoint) {
    desktopFlg = false;
    smartphoneFlg = true;
    $('body').removeClass('desktop').addClass('smartphone');
  } else {
    desktopFlg = true;
    smartphoneFlg = false;
    $('body').addClass('desktop').removeClass('smartphone');
  }

}



// load判定関数（PC,SP共通処理）
//-------------------------------------------------------------
function loadedPageFunc (){

  var $pageBody = $('body');
  $pageBody.addClass('loaded');

}



// アコーディオン処理（個別処理、PC,SP共通処理）
// （class名を指定するとその次の要素がアコーディオン処理をする）
//-------------------------------------------------------------
function showAccordionFunc($accodionClassName){

  var $accodionClassName = $($accodionClassName);
  $accodionClassName.next('*').hide();
  $accodionClassName.click(function() {
    if($(this).hasClass('show-accordion')){
      $(this).removeClass('show-accordion').next('*').slideUp();
    } else {
      $(this).addClass('show-accordion').next('*').slideDown();
    }
  });

}


// アコーディオン処理（一括処理、PC,SP共通処理）
// （dl > dt dd での処理を想定とする　dtをクリックした時にddをアコーディオン処理）
//-------------------------------------------------------------
function showAllAccordionFunc($accodionAllClassName){

  var $accodionAllClassName = $($accodionAllClassName + ' dt');

  $accodionAllClassName.click(function() {
    if($(this).hasClass('show')){
      $(this).removeClass('show').parent('dl').children('dd').slideUp('fast');
    } else {
      // 常に一つだけの処理
      $accodionAllClassName.removeClass('show');
      $(this).addClass('show').parent('dl').children('dd').slideUp('fast');
      $(this).next('dd').slideDown('fast');
      // 個別に処理する場合（デフォルトコメントアウト）
      // $(this).addClass('show').next('dd').slideDown('fast');
    }
  });

}


// TAB処理（PC,SP共通処理）
// タブリストとタブコンテンツが必要
// 引数で タブリストのclass名とタブコンテンツのclass名が必須となる。
//-------------------------------------------------------------
function showTabFunc($tabChooseClassName,$tabContentsClassName){

  var $tabChooseClassName = $($tabChooseClassName + '> *');
  var $tabContentsClassName = $($tabContentsClassName + '> *');

  var tab = $tabChooseClassName,
      tabChild = $tabContentsClassName,
      url = location.href,
      hash = [];
      hash = new Array();
      hash = url.split('#');

  if(hash[1]){
    var indexId = tab.index($('.' + hash[1]));
    tab.eq(indexId).addClass('show-tab');
    tabChild.hide().eq(indexId).show().addClass('show-tab-child');
  } else {
    tab.eq(0).addClass('show-tab');
    tabChild.hide().eq(0).show().addClass('show-tab-child');
  }
  tab.click(function() {
    var index = tab.index(this);
    tab.removeClass('show-tab');
    $(this).addClass('show-tab');
    tabChild.hide().removeClass('show-tab-child').eq(index).show().addClass('show-tab-child');
  });

}


//page top関数（PC,SP共通処理）
//-------------------------------------------------------------
function goToPageTopFunc($pageTopId){

  var $pageTopId = $($pageTopId);
  $pageTopId.click(function() {
    $("html, body").animate({scrollTop:0}, 500, "swing");
    return false;
  });

}


//ページ内スクロール関数（PC,SP共通処理）
//-------------------------------------------------------------
function smoothScrollMoveFunc($goToClassName){

  var $goToClassName = $($goToClassName);
  $goToClassName.click(function(){
    var speed = 500;
    var href= $(this).attr("href");
    var target = $(href == "#" || href == "" ? 'html' : href);
    var position = target.offset().top;
    $("html, body").animate({scrollTop:position}, speed, "swing");
    return false;
  });

}

//GET値 取得（PC,SP共通処理）
//-------------------------------------------------------------

function GetQueryString()
{
    var result = {};
    if( 1 < window.location.search.length )
    {
        // 最初の1文字 (?記号) を除いた文字列を取得する
        var query = window.location.search.substring( 1 );

        // クエリの区切り記号 (&) で文字列を配列に分割する
        var parameters = query.split( '&' );

        for( var i = 0; i < parameters.length; i++ )
        {
            // パラメータ名とパラメータ値に分割する
            var element = parameters[ i ].split( '=' );

            var paramName = decodeURIComponent( element[ 0 ] );
            var paramValue = decodeURIComponent( element[ 1 ] );

            // パラメータ名をキーとして連想配列に追加する
            result[ paramName ] = paramValue;
        }
    }
    return result;
}



//TOP PAGE スライド関数
//-------------------------------------------------------------
function showTopPageSliderFunc(){

  var pagerTxtArry = [];
  $('#sliderCalender li .calender-block .js-month-title').each(function(){
    if($(this).parent('li').hasClass('bx-clone')){
    }else{
      pagerTxtArry.push($(this).text());
    }
  });

  
  function bxControlCopyFunc(){
    $('#copyBxControl .bx-controls').clone(true).appendTo('#copyBxControl .bx-wrapper');
  }

  var pageTopPageObj = new Object();

  pageTopPageObj.topSlideFunc = function (){
    $('#sliderTop').bxSlider({
      auto: 'true',
      nextText: '',
      prevText: ''
    });
  }

  pageTopPageObj.spMainSlideFunc = function (){

  var slideIdQuery = GetQueryString();
  var slideId = slideIdQuery['slideId'];
  var mainSlider = $('#sliderCalender').bxSlider({
      nextText: '次の月',
      prevText: '前の月',
      adaptiveHeight: true,
      touchEnabled: true,
       buildPager: function(slideIndex){
        switch(slideIndex){
          case 0: return pagerTxtArry[0];
          case 1: return pagerTxtArry[1];
          case 2: return pagerTxtArry[2];
          case 3: return pagerTxtArry[3];
          case 4: return pagerTxtArry[4];
          case 5: return pagerTxtArry[5];
          case 6: return pagerTxtArry[6];
          case 7: return pagerTxtArry[7];
          case 8: return pagerTxtArry[8];
          case 9: return pagerTxtArry[9];
          case 10: return pagerTxtArry[10];
          case 11: return pagerTxtArry[11];
          case 12: return pagerTxtArry[12];
        }
      }
    });

    if(slideId){
      if(slideId == 0){
        // 0の値が来た時には何もデフォルト表示
      }else{
        mainSlider.goToSlide(slideId);
      }
    }

    bxControlCopyFunc();
    // makeSpCalenderLinkFunc();


  }


pageTopPageObj.pcMainSlideFunc = function (){

  var slideIdQuery = GetQueryString();
  var slideId = slideIdQuery['slideId'];

  var mainSlider = $('#sliderCalender').bxSlider({
      nextText: '次の月',
      prevText: '前の月',
      adaptiveHeight: true,
      touchEnabled: false,
       buildPager: function(slideIndex){
        switch(slideIndex){
          case 0: return pagerTxtArry[0];
          case 1: return pagerTxtArry[1];
          case 2: return pagerTxtArry[2];
          case 3: return pagerTxtArry[3];
          case 4: return pagerTxtArry[4];
          case 5: return pagerTxtArry[5];
          case 6: return pagerTxtArry[6];
          case 7: return pagerTxtArry[7];
          case 8: return pagerTxtArry[8];
          case 9: return pagerTxtArry[9];
          case 10: return pagerTxtArry[10];
          case 11: return pagerTxtArry[11];
          case 12: return pagerTxtArry[12];
        }
      }
    });
    if(slideId){
      if(slideId == 0){
        // 0の値が来た時には何もデフォルト表示
      }else{
        mainSlider.goToSlide(slideId);
      }
    }

    bxControlCopyFunc();

  }

  return pageTopPageObj;

}
//iframe 高さ親HTMLに反映
//-------------------------------------------------------------
function getIframeFunc(){
  
  $("#parentIframe", window.parent.document).height(document.body.scrollHeight);
  iframeHeight = document.body.scrollHeight;
  $('#modalWrapOuter', window.parent.document).css('height',iframeHeight+200+'px');
}

//汎用シート詳細ポップアップ関数(PC)
//-------------------------------------------------------------
function showPopupPcSeatDetailFunc($targetClassName){

  var showPopuFlg = false;
  var $targetClassName = $($targetClassName);
  var modalHeight = $('.modal-wrap').outerHeight(true);
  var winHeight = window.innerHeight;
  var nowY = y;
  var outerCommonHeight = 0;

  if(modalHeight > winHeight){
    outerCommonHeight = modalHeight;
  }else if(modalHeight < winHeight){
    outerCommonHeight = winHeight;
  }

  $targetClassName.click(function(){
    console.log(outerCommonHeight);
    showPopuFlg = true;

    var loadUrl = $(this).data('url');
    if(loadUrl){
      $('#loadFrameArea iframe').attr('src' , loadUrl);
    }

    if(showPopuFlg){
      $('.modal-out-wrap').addClass('show');
      

      $('body').scrollTop(0);
      $('.page').css({
        'overflow-y':'hidden',
        'height': outerCommonHeight+'px',
        'min-width' : '1000px'
      });

      $('.modal-out-wrap').css('height',outerCommonHeight+'px');

    }

    positionCenterModal();
    
    return false;
    
  });

  $('#closeBtn, #modalWrapOuter').click(function(){
    $('.modal-out-wrap').removeClass('show');
    $('body').scrollTop(nowY);
    $('.page').css({
      'overflow-y':'auto',
      'height':'auto'
    });
    $('.modal-out-wrap').css('height','auto');
    showPopuFlg = false;
    return false;
  }); 


}


//汎用シート詳細ポップアップ関数(SP)
//-------------------------------------------------------------
function showPopupSpSeatDetailFunc($targetClassName){
  var thisModalWrapHeight = $('#modalWrapOuter').outerHeight(true);
  var showPopuFlg = false;
  var $targetClassName = $($targetClassName);
  var nowY = y;

  $targetClassName.click(function(){
  showPopuFlg = true;

    var loadUrl = $(this).data('url');
    if(loadUrl){
      $('#loadFrameArea iframe').attr('src' , loadUrl);
    }
   
    if(showPopuFlg){
      $('.modal-out-wrap').addClass('show');
      var modalHeight = 5000;
      $('body').scrollTop(0);
      $('.page').css({
        'overflow-y':'hidden'
      });
      $('#modalWrapOuter, .page').css('height',thisModalWrapHeight+'px');
    }

    positionCenterModal();
    
    return false;
    
  });

  $('#closeBtn, #modalWrapOuter').click(function(){
    event.preventDefault();
    console.log(y);
    $('.modal-out-wrap').removeClass('show');
    $('body').scrollTop(nowY);
    $('.page').css({
      'overflow':'scroll',
      'height':'auto'
    });
    $('.modal-out-wrap').css('height','auto');
    showPopuFlg = false;

  });  
}


//センタリングをする関数
function positionCenterModal(){

    //画面(ウィンドウ)の幅、高さを取得
    var w = $(window).width();
    var h = $(window).height();
    var cw = $("#modalWrap").outerWidth();
    var ch = $("#modalWrap").outerHeight();
    console.log(cw);
    if(desktopFlg){
      if(w < 1100){
        $('.modal-wrap').css('width', '1020px');
         $("#modalWrap").css({"left": ((w - cw)/2) + "px"});

      }else if(w > 1100 && w < 1170){
         $('.modal-wrap').css('width', '93%');
       $("#modalWrap").css({"left": ((w - cw)/2) + "px"});

      }else if(w > 1170){
       $('.modal-wrap').css('width', '90%');
       $("#modalWrap").css({"left": ((w - cw)/2) + "px"});

      }
    }else{
      $("#modalWrap").css({"left": ((w - cw)/2) + "px"});
    }

}



//汎用シート金額表示関数
//-------------------------------------------------------------
function moveSeatDetailAllFunc(){

  $("#goToSeatPrice li a").click(function(){
    var target = $(this).attr('href');
    var fillTarget = target.split("seat");
    // IDでは重複した場合対応できないので、class名に一部変更
    var fillTargetClass = '.seat-'+fillTarget[1];
    var th = $(target).position();
    var sh = $("#seatPriceTargetWrap").scrollTop();
    var pos = th.top + sh -200;
    $("#goToSeatPrice li a").removeClass('now-cursor');
    $(this).addClass('now-cursor');

    if(desktopFlg){
      $("#seatPriceTargetWrap").animate({
        scrollTop: pos
      },300, "swing");    
    }else if(smartphoneFlg){
      $( 'html,body', window.parent.document).animate({
        scrollTop: pos - sh + 260
      },300, "swing");   
    }
    
    $('.price-table tr').removeClass('show-price');
    $(fillTargetClass).parent('tr').addClass('show-price');
    return false;

  });

  $('#seatPriceTarget tr')
    // マウスポインターが画像に乗った時の動作
    .mouseover(function(e) {
      var thisNumber = $(this).children('.number').attr('id');
      if(thisNumber != 'undefined'){
        $('#goToSeatPrice li#'+thisNumber+'Number a').addClass('now-cursor');
      }
      $(this).addClass('now-cursor');
    })
    // マウスポインターが画像から外れた時の動作
    .mouseout(function(e) {
      console.log('out');
      $('#goToSeatPrice li a').removeClass('now-cursor');
      $(this).removeClass('now-cursor');
    });


    $("#goToPriceTableTop").click(function(){
      if(desktopFlg){
          $("#seatPriceTargetWrap").animate({
            scrollTop: 0
          },300, "swing");
      }else if(smartphoneFlg){
          $( 'html,body', parent.document).animate({
            scrollTop: 0
          },300, "swing");
      }
    });

}


//ハンバーガーメニュー 用関数
//-------------------------------------------------------------
function showGlobalMenuFunc(){
  var showFlg = false;
  $('#showBtn button').click(function(){
    $(this).parent('#showBtn').toggleClass('show');
    $('body').toggleClass('body-fixed');  
    // return false;
  });
}


//チケット情報のみハンバーガーメニュー 用関数
//-------------------------------------------------------------
function showTicketMenuFunc(){
  var showFlg = false;
  $('#showTicketModal').click(function(){
    $('#showBtn').toggleClass('show');
    $('body').toggleClass('body-fixed');  
    $('body').toggleClass('ticket-menu');     
    return false;
  });
    $('#showBtn button').on('click',function(){
      $('body').removeClass('ticket-menu'); 
    });

}



//汎用ハンバーガーメニュー内開閉メニュー
//-------------------------------------------------------------
function showSubMenuFunc(){
  $('.js-has-sub-menu').click(function(){
    $(this).parent('li').toggleClass('show-sub-menu');
    return false;
  });
}


//ticket PAGE 用関数
//-------------------------------------------------------------
function showTicketPageSliderFunc(){
var w = $(window).width();
var x = 480;
if (w >= x) {var num = 6} else { var num = 2};
  $('#sliderTicket').bxSlider({
      auto: 'true',
      nextText: '',
      prevText: '',
      pager: false,
      maxSlides: num,
      minSlides: num,
      slideWidth: 250,
      slideMargin: 10,
      moveSlides: 1,
      slideMargin: 10
    });
}


// SPログイン系アコーディオン処理（SP処理）
//-------------------------------------------------------------
function showSploginAreaAccordionFunc($accodionClassName){

  // var $accodionClassName = $($accodionClassName + ' h3');

  $('.js-sp-accotdion-btn h3, .js-show-box a').click(function() {
    $(this).parents('td').toggleClass('show');
    return false;
  });

}

function attentionCommponBoxFunc($targetIdName){
  var $targetIdName = $($targetIdName);
  $targetIdName.click(function() {
    $(this).parent('#attentionCommon').hide();
    return false;
  });
  
}


// SPECIAL SPモーダル高さHTMLに反映
//-------------------------------------------------------------
function getSpModalFunc(){

  var thisModalWrapHeight = $('#modalWrapOuter').outerHeight(true);
  $('#modalWrapOuter, .page').css('height',thisModalWrapHeight+'px');

}

function hiddenSpecialMenuFunc(){
  $('.humberger-menu-list-box li:first-child, #showTicketModal').hide();
}


// ============================================================
// ATTENTION & COMMON RULE!!
// まとめて関数実行（※必要に応じて条件分岐を入れる）
// ページ個別に処理をする場合は「ページ固有のID名.lengthで処理を分岐」
// PC、SP、iPadで処理を分ける場合は①の関数を参照して処理を分岐
// ============================================================

// コンストラクタ関数の実行
if($('#topPage').length || $('#farmPage').length){
  var pageTopPageObj = showTopPageSliderFunc();
}

// スクロール処理
window.addEventListener( "scroll", function() {
  y = window.pageYOffset;
      // console.log(y);
});

// ページの全データを読み込み後
$(window).on('load', function() {

  loadedPageFunc();
  checkDeviceAndWidthFunc();

});

// リサイズが走った場合
$(window).on('resize', function(){

  checkDeviceAndWidthFunc();
  positionCenterModal();

});

// DOM生成後
$(function(){

  // 共通処理
  checkDeviceAndWidthFunc();
  goToPageTopFunc('#pageTop');
  smoothScrollMoveFunc('a.scroll');
  showAccordionFunc('.js-accordion');
  showAllAccordionFunc('.js-all-accordion');
  showTabFunc('.js-tab','.js-tab-child');
  showGlobalMenuFunc();
  showTicketMenuFunc();
  showSubMenuFunc();
  showSploginAreaAccordionFunc();
  attentionCommponBoxFunc('#attentionCloseBtn');

  // TOP PAGE
  if($('#topPage').length){
 
    if(smartphoneFlg){
      pageTopPageObj.spMainSlideFunc();
      pageTopPageObj.topSlideFunc();
      // makeSpCalenderLinkFunc();
      
    }else if(desktopFlg){
      pageTopPageObj.pcMainSlideFunc();
      pageTopPageObj.topSlideFunc();
      showPopupPcSeatDetailFunc('.js-show-pooup-detail-seat');
    }
  }
  // FARM PAGE 
  if($('#farmPage').length){
 
    if(smartphoneFlg){
      pageTopPageObj.spMainSlideFunc();
      // makeSpCalenderLinkFunc();
    }else if(desktopFlg){
      pageTopPageObj.pcMainSlideFunc();
      showPopupPcSeatDetailFunc('.js-show-pooup-detail-seat');
    }
  }

  // SEAT PAGE 
  if($('#seatPage').length){
    if(smartphoneFlg){
      showPopupSpSeatDetailFunc('.js-show-pooup-detail-seat');
    }
  }

  // ticket PAGE
  if($('#ticketPage').length){
    showTicketPageSliderFunc();
  }

  // POP UP PRICE PAGE
  if($('#popUpDetail').length){
    moveSeatDetailAllFunc();
    if(smartphoneFlg){
      getIframeFunc();
      console.log('cje');
    }
  }

  // PAYMENT PAGE
  if($('#paymentPage').length){
    $('.payment-flow li').matchHeight();
  }

  // SPECIAL PAGE 
  if($('#specialPage').length){
    hiddenSpecialMenuFunc();   
    if(smartphoneFlg){
      showPopupSpSeatDetailFunc('.js-show-pooup-detail-seat');   
      // getSpModalFunc();
        
    }else if(desktopFlg){
      showPopupPcSeatDetailFunc('.js-show-pooup-detail-seat');
    }
  }  

});
