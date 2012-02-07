if(!widget){
    throw "widget module is not found";
}

(function(widget){
    var _has_click_event = null;

    var on_dialog = function(we){
        var dialog = we.get_dialog();
        _has_click_event = "#@id@ img".replace("@id@", dialog.attr("id"));
        $(document).on("click", _has_click_event, function(){
            we.close_dialog(this);
        });
        
        we.attach_hightlight(_has_click_event);
        
        var expr = "img[src='@src@']".replace("@src@", we.get_data().imagefile)
        we.attach_managed(dialog_elt.find(expr));
    };

    var on_selected = function(we){
        _has_click_event.die();
        we.close_dialog();
    };

    var collect_data = function(we, choiced_elt){
        return {imagefile: $(choiced_elt).attr("src")};
    };

    return widget.include("image", {
        on_dialog: on_dialog, 
        on_selected: on_selected, 
        collect_data: collect_data
    });
})(widget); // widget is ok?
