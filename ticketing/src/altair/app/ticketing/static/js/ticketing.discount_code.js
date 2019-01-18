/**
 * 「？」マーククリックによるヘルプ表示
 */
function popOver() {
    "use strict";
    $('[rel=popover]').popover({html: true});
}

/**
 * モーダルウィンドウ表示
 * href属性で指定したURLのレンダリング結果をロードする
 */
function ajaxModal() {
    "use strict";
    $("a.ajax-modal[data-toggle=modal]").click(function () {
        let wrap = $($(this).attr("data-target"));
        wrap.empty();
        if ($(this).data("preload")) {
            $(this).data("preload")($(wrap).load.bind($(wrap), $(this).attr("href")));
        } else {
            $(wrap).load($(this).attr("href"));
        }
    });
}