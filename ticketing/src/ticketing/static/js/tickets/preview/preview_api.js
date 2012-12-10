// backbone
function svg_preview($el, apiurl, svg){
    $.post(apiurl, {"svg": svg}).done(function(data){
        if(data.status){
            $el.empty();
            var imgdata = "data:image/png;base64,"+data.data;
            var preview_img = $("<img title='preview' alt='preview todo upload file'>").attr("src", imgdata);
            $el.append(preview_img);
        } else {
            alert(data.message);
        }
    }).fail(function(s, err){alert(s.responseText)});
}