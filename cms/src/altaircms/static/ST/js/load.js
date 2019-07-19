$(function(){
    var ua = navigator.userAgent;
    var retinaSwitch = window.devicePixelRatio;

    if((ua.indexOf('iPhone') > 0) || ua.indexOf('iPod') > 0 || (ua.indexOf('Android') > 0 && ua.indexOf('Mobile') > 0)){
        $('head').prepend('<meta name="viewport" content="width=device-width,initial-scale=1">');
    } else {
        $('head').prepend('<meta name="viewport" content="width=1160">');
    }
});

$(function () {
    var ua = navigator.userAgent;
    if (ua.indexOf('iPhone') > 0 || ua.indexOf('Android') > 0 && ua.indexOf('Mobile') > 0) {
        // スマートフォン用コード

        $('.topMainSlider_box').slick({
            autoplay:true,
            autoplaySpeed:3000,
            dots:true,
            slidesToShow:3,
            slidesToScroll:1,

          responsive: [{
            breakpoint: 750,  //ブレイクポイントを指定
            settings: {
              centerMode: true, //要素を中央寄せにする
              slidesToShow:1,
              slidesToScroll:1,
              centerPadding:"20px",
            }
          }]
        });

        $('.topFavoritesSlider').slick({
            autoplay:true,
            autoplaySpeed:3000,
            slidesToShow:1,
            slidesToScroll:1,
            centerMode: true, //要素を中央寄せにする
            centerPadding:"80px",

        });

		window.location.href = "#";
    } else {


        $('.topMainSlider_box').slick({
            autoplay:true,
            autoplaySpeed:3000,
            dots:true,
            slidesToShow:3,
            slidesToScroll:1,

          responsive: [{
            breakpoint: 750,  //ブレイクポイントを指定
            settings: {
              centerMode: true, //要素を中央寄せにする
              slidesToShow:1,
              slidesToScroll:1,
              centerPadding:"20px",
            }
          }]
        });
        $('.topSlider').slick({
            autoplay:true,
            autoplaySpeed:3000,
            slidesToShow:4,
            slidesToScroll:1,
        });
        $('.topFavoritesSlider').slick({
            autoplay:true,
            autoplaySpeed:3000,
            slidesToShow:6,
            slidesToScroll:1,
        });

    }
})