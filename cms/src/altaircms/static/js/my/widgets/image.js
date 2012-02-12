if(!widget){
    throw "widget module is not found";
}

(function(widget){
    var opt = {} //widget local variable
    var _has_click_event = null;

    var load_page = function(we){
        return we.dialog.load("/sample/api/load/widget/image");
    };

    var on_dialog = function(we){
        _has_click_event = "#@id@ img".replace("@id@", we.dialog .attr("id"));
        $(document).on("click", _has_click_event, function(){
            we.finish_dialog(this);
        });
        
        we.attach_highlight(_has_click_event);
        var expr = "img[src='@src@']".replace("@src@", we.get_data(we.where).imagefile)
        we.attach_managed(we.dialog.find(expr));
    };

    var on_close = function(we){
        $(document).off("click", _has_click_event);
    };

    var collect_data = function(we, choiced_elt){
        var choiced_elt = $(choiced_elt);
        return {imagefile: choiced_elt.attr("src"), 
                pk: choiced_elt.attr("pk")};
    };
    
    return widget.include("image", {
        load_page: load_page, 
        on_dialog: on_dialog, 
        on_close: on_close, 
        collect_data: collect_data, 
        save_url: "/sample/api/save/widget"
    });
})(widget); 
