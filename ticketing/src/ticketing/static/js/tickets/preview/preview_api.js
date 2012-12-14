function svg_preview($el, apiurl, svg, ticket_format){
    $.post(apiurl, {"svg": svg, "ticket_format": ticket_format}).done(function(data){
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