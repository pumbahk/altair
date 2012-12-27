// api-params: {svg: <>,  ticket_format: <>,  model_name: <>,  model: <>}
function svg_preview($el, apiurl, params){
    $.post(apiurl, params).done(function(data){
        if(data.status){
            $el.empty();
            var imgdata = "data:image/png;base64,"+data.data;
            var preview_img = $("<img title='preview' alt='preview todo upload file'>").attr("src", imgdata);
            $el.append(preview_img);
        } else {
            alert(data.message);
        }
    }).fail(function(s, err){alert(s.responseText)});
};

// use: static/js/spin.js
// use: static/js/altair/spinner.js
// use: static/js/tickets/modal/api.js
function svg_preview_component($el, $modalArea, apiurl){
    return new modal.api.AjaxModalView({
        el: $el, 
        href: apiurl, 
        modalArea: $modalArea, 
        option: {backdrop: false}, 
    });
};