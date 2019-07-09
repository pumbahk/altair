$(function(){
  $('a[href^="#"]').click(function() {
      var speed = 400;
      var href= $(this).attr("href");
      var target = $(href == "#" || href == "" ? 'html' : href);
      var position = target.offset().top;
      $('body,html').animate({scrollTop:position}, speed, 'swing');
      return false;
   });
});


//隣接高さ揃える（matchheight.js）
$(function(){
  $('').matchHeight();
});

$(function(){
  $('.HamburgerWrap').click(function() {
    $('.smpNav').toggleClass("on");
  });
  $('.searchSmpwrap').click(function() {
    $('#search').addClass("searchOn");
  });
  $('.smpClose').click(function() {
    $('#search').removeClass("searchOn");
  });
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