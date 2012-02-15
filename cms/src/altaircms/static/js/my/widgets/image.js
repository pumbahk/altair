if(!widget){
    throw "widget module is not found";
}

// load_page はCoCに紐つけることも加納だな。
// 逆にsave_dataが内部で紐づいちゃっている

(function(widget){
    var opt = {} //widget local variable
    var _has_click_event = null;

    var load_page = function(we){
        return we.dialog.load("/api/widget/image_widget/dialog");
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
                asset_id: choiced_elt.attr("pk")};
    };

    var save_data = function(params){
        
    };
    return widget.include("image", {
        load_page: load_page, 
        on_dialog: on_dialog, 
        on_close: on_close, 
        collect_data: collect_data, 
        save_data: save_data, 
    });
})(widget); 
