$(document).ready(function(){
  //acordion_treeを一旦非表示に
  $(".acordion_tree").css("display","none");
  //triggerをクリックすると以下を実行
  $(".trigger").click(function(){
    //もしもクリックしたtriggerの直後の.acordion_treeが非表示なら
    if($("+.acordion_tree",this).css("display")=="none"){
         //直後のacordion_treeをスライドダウン
         $("+.acordion_tree",this).slideDown("normal");
  }else{
    //クリックしたtriggerの直後の.acordion_treeが表示されていればスライドアップ
    $("+.acordion_tree",this).slideUp("normal");
  }
		$(".acordion_tree").not($(this).next(".acordion_tree")).slideUp();
		$(this).siblings('.trigger').removeClass('active');
		$(this).toggleClass('active');
  });
});

$(document).ready(function(){
  //acordion_treeを一旦非表示に
  $(".acordion_treeA").css("display","none");
  //triggerをクリックすると以下を実行
  $(".triggerA").click(function(){
    //もしもクリックしたtriggerの直後の.acordion_treeが非表示なら
    if($("+.acordion_treeA",this).css("display")=="none"){
         //直後のacordion_treeをスライドダウン
         $("+.acordion_treeA",this).slideDown("normal");
  }else{
    //クリックしたtriggerの直後の.acordion_treeが表示されていればスライドアップ
    $("+.acordion_treeA",this).slideUp("normal");
  }
		$(".acordion_treeA").not($(this).next(".acordion_treeA")).slideUp();
		$(this).siblings('.triggerA').removeClass('active');
		$(this).toggleClass('active');
  });
});