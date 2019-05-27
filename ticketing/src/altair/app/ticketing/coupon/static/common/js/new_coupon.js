$(document).on('click', '#modal-close, #modal-overlay', function () {
    $("#modal-close, #modal-overlay").off("click");
    $("#modal-overlay").remove();
    $("#modal-content").css("display", "none");
    $("#alert-modal-content").css("display", "none");
});

function check_can_use_coupon(check_url) {
    return $.ajax({
        type: 'GET',
        url: check_url
    })
}

$(document).on('click', '.coupon_button', function () {
    var next_url = $(this).attr("next_url");
    var check_url = $(this).attr("check_url");

    check_can_use_coupon(check_url).done(function (result) {
        if (result == true) {
            console.log("coupon is not used");
            $(this).blur();
//現在のモーダルウィンドウを削除して新しく起動する
            if ($("#modal-overlay")[0]) $("#modal-overlay").remove();

            $("body").append('<div id="modal-overlay"></div>');
            $("#modal-overlay").fadeIn("slow");
            $("#modal-content").fadeIn("slow");

// couponを使用するurl設定
            $('#coupon_form').attr("action", next_url);

            centeringModalSyncer($("#modal-content"));
        } else {
            console.log("coupon is used");
            $(this).blur();
//現在のモーダルウィンドウを削除して新しく起動する
            if ($("#modal-overlay")[0]) $("#modal-overlay").remove();

            $("body").append('<div id="modal-overlay"></div>');
            $("#modal-overlay").fadeIn("slow");
            $("#alert-modal-content").fadeIn("slow");

            centeringModalSyncer($("#alert-modal-content"));
        }
    }).fail(function (result) {
    });
});

function centeringModalSyncer(content) {
    var w = $(window).width();alert-modal-content
    var h = $(window).height();
    var cw = content.outerWidth({margin: true});
    var ch = content.outerHeight({margin: true});
    var pxleft = ((w - cw) / 2);
    var pxtop = ((h - ch) / 2);
    content.css({"left": pxleft + "px"});
    content.css({"top": pxtop + "px"});
}

function set2fig(num) {
    // 桁数が1桁だったら先頭に0を加えて2桁に調整する
    var ret;
    if( num < 10 ) { ret = "0" + num; }
        else { ret = num; }
        return ret;
}

function showClock2() {
    var nowTime = new Date();
    var nowyear = nowTime.getFullYear();
    var nowmonth = set2fig(nowTime.getMonth() + 1);
    var nowdate = set2fig(nowTime.getDate());

    var nowHour = set2fig(nowTime.getHours());
    var nowMin  = set2fig(nowTime.getMinutes());
    var nowSec  = set2fig(nowTime.getSeconds());

    var msg =  nowyear + "年" + nowmonth + "月" + nowdate + "日" + "  " + nowHour + ":" + nowMin + ":" + nowSec;
    $("#realtime-clock").html(msg);
}

$(document).ready(function () {
    setInterval('showClock2()',1000);
    $("#btnAllCoupon").hide();
    $(window).on("scroll", function () {
        if ($(this).scrollTop() > 50) {
            $("#btnAllCoupon").fadeIn("fast");
        } else {
            $("#btnAllCoupon").fadeOut("fast");
        }
        scrollHeight = $(document).height();
        scrollPosition = $(window).height() + $(window).scrollTop();
        footHeight = $("footer").innerHeight();
        if (scrollHeight - scrollPosition <= footHeight) {
            $(".btnAllCoupon").css({
                "position": "fixed",
                "bottom": footHeight + 5
            });
        } else {
            $(".btnAllCoupon").css({
                "position": "fixed",
                "bottom": "5px"
            });
        }
    });
    $('#btnAllCoupon').click(function () {
        $('body,html').animate({
            scrollTop: 0
        }, 400);
    });
});

if (document.cookie.indexOf("_coupon") > -1) {
    $(".confirm_exist").hide();
    $(".confirm_not_exist").show();
} else {
    $(".confirm_exist").show();
    $(".confirm_not_exist").hide();
}
