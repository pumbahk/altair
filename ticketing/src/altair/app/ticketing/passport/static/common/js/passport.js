$(document).on('click', '#modal-close, #modal-overlay', function () {
    $("#modal-close, #modal-overlay").off("click");
    $("#modal-overlay").remove();
    $("#modal-content").css("display", "none");
    $("#alert-modal-content").css("display", "none");
});

function check_can_use_passport(check_url) {
    return $.ajax({
        type: 'GET',
        url: check_url
    })
}

$(document).on('click', '.passport_button', function () {
    var next_url = $(this).attr("next_url");
    var check_url = $(this).attr("check_url");

    console.log("zzz");
    check_can_use_passport(check_url).done(function (result) {
        if (result == true) {
            console.log("passport is not used");
            $(this).blur();
//現在のモーダルウィンドウを削除して新しく起動する
            if ($("#modal-overlay")[0]) $("#modal-overlay").remove();

            $("body").append('<div id="modal-overlay"></div>');
            $("#modal-overlay").fadeIn("slow");
            $("#modal-content").fadeIn("slow");

// passportを使用するurl設定
            $('#passport_form').attr("action", next_url);

            centeringModalSyncer($("#modal-content"));
        } else {
            console.log("passport is used");
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
    var w = $(window).width();
    var h = $(window).height();
    var cw = content.outerWidth({margin: true});
    var ch = content.outerHeight({margin: true});
    var pxleft = ((w - cw) / 2);
    var pxtop = ((h - ch) / 2);
    content.css({"left": pxleft + "px"});
    content.css({"top": pxtop + "px"});
}

$(document).ready(function () {
    $("#btnAllPassport").hide();
    $(window).on("scroll", function () {
        if ($(this).scrollTop() > 50) {
            $("#btnAllPassport").fadeIn("fast");
        } else {
            $("#btnAllPassport").fadeOut("fast");
        }
        scrollHeight = $(document).height();
        scrollPosition = $(window).height() + $(window).scrollTop();
        footHeight = $("footer").innerHeight();
        if (scrollHeight - scrollPosition <= footHeight) {
            $(".btnAllPassport").css({
                "position": "fixed",
                "bottom": footHeight + 5
            });
        } else {
            $(".btnAllPassport").css({
                "position": "fixed",
                "bottom": "5px"
            });
        }
    });
    $('#btnAllPassport').click(function () {
        $('body,html').animate({
            scrollTop: 0
        }, 400);
    });
});

var required_confirm = null;
if (document.cookie.indexOf("_passport") > -1) {
    $(".confirm_exist").hide();
    $(".confirm_not_exist").show();
} else {
    $(".confirm_exist").show();
    $(".confirm_not_exist").hide();
}
