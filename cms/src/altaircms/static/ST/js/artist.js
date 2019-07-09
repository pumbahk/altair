$(function(){
  $('.artist_PerformanceWrapEnd dt p').click(function() {
    $('.artist_PerformanceWrapEnd dd').slideToggle();
    $('.artist_PerformanceWrapEnd').toggleClass("on");
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