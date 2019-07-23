$(function(){
  $('.artist_PerformanceWrapEnd dt p').click(function() {
    $('.artist_PerformanceWrapEnd dd').slideToggle();
    $('.artist_PerformanceWrapEnd').toggleClass("on");
  });

  $('.artist_Performance .artist_PerformanceList').click(function() {
         $(this).parent().find('.more').slideToggle()
  });
  $('.artist_Performance .more .close').click(function() {
         $(this).parent().slideToggle()
  });

});



$(function () {
    var ua = navigator.userAgent;
    if (ua.indexOf('iPhone') > 0 || ua.indexOf('Android') > 0 && ua.indexOf('Mobile') > 0) {
        // スマートフォン用コード
        $('.artistRecommendSlider').slick({
            autoplay:true,
            autoplaySpeed:3000,
            slidesToShow:1,
            slidesToScroll:1,
            centerMode: true, //要素を中央寄せにする
            centerPadding:"80px",

        });
    } else {
        $('.artistRecommendSlider').slick({
            autoplay:true,
            autoplaySpeed:3000,
            slidesToShow:6,
            slidesToScroll:1,
        });

    }
})