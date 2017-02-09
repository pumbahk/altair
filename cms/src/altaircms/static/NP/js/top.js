

// アコーディオン処理（個別処理、PC,SP共通処理）
// （class名を指定するとその次の要素がアコーディオン処理をする）
//-------------------------------------------------------------
function gameListClickAreaSpFunc($accodionClassName){

  $('.calender-tbl td.price .js-show-pooup-detail-seat').each(function(){
    $(this).clone().insertAfter(this);
  });
  $('.calender-tbl td.price .js-show-pooup-detail-seat:nth-child(2)').each(function(){
    $(this).removeClass('js-show-pooup-detail-seat');
  });
  $('.calender-tbl td.price .js-show-pooup-detail-seat:nth-child(1)').each(function(){
    $(this).addClass('click-area');
  });
  $('.calender-tbl td.price .click-area').each(function(){
    var thisClickHeight = $(this).parents('tr').height();
    console.log(thisClickHeight);
    $(this).css('height',thisClickHeight+'px');
  });

}



// ============================================================
// ATTENTION & COMMON RULE!!
// まとめて関数実行（※必要に応じて条件分岐を入れる）
// ページ個別に処理をする場合は「ページ固有のID名.lengthで処理を分岐」
// PC、SP、iPadで処理を分ける場合は①の関数を参照して処理を分岐
// ============================================================



// DOM生成後
$(function(){

  // TOP PAGE
  if($('#topPage').length){
 
    if(smartphoneFlg){
      
      gameListClickAreaSpFunc();
      
    }else if(desktopFlg){
      
    }
  }
 

});
