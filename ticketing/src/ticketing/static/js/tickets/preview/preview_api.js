// use: static/js/spin.js
// use: static/js/altair/spinner.js
// api-params: {svg: <>,  ticket_format: <>,  model_name: <>,  model: <>}
var svg_preview = (function(){
    var sejPreviewConnectOK = null;
    var sejConnectConfirm = function(){
        if(sejPreviewConnectOK != null){
            return sejPreviewConnectOK;
        }
        var sejConfirmMessage = "sejのpreview serverと通信します。preview結果を表示するまで時間が掛かりそうですがよろしいですか？";
        sejPreviewConnectOK = window.confirm(sejConfirmMessage);
        return sejPreviewConnectOK;
    };

    return function($el, apiurl, params){
        if (params.type == "sej" && !sejConnectConfirm()){
            return;
        }
        $el.spin("large");
        $.post(apiurl, params).done(function(data){
            if(data.status){
                $el.empty();
                var imgdata = "data:image/png;base64,"+data.data;
                var preview_img = $("<img title='preview' alt='preview todo upload file'>").attr("src", imgdata);
                $el.append(preview_img);
            } else {
                $el.empty();
                $el.text("通信に失敗しました。preview画像を表示することができません。");
            }
            $el.spin(false);
        }).fail(function(s, err){
            $el.empty();
            $el.text("通信に失敗しました。preview画像を表示することができません。");
        });
    }
})();

// use: static/js/spin.js
// use: static/js/altair/spinner.js
// use: static/js/tickets/modal/api.js
function svg_preview_component($el, $modalArea, apiurl, callback){
    return new modal.api.AjaxModalView({
        el: $el, 
        href: apiurl, 
        modalArea: $modalArea, 
        option: {backdrop: false}, 
        callback: callback
    });
};