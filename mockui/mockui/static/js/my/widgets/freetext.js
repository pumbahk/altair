    if(!widget){
        throw "widget module is not found";
    }

(function(widget){
    var _has_click_event = null;
    var is_initialized = false;
    var _initialize = function(){
        if(!is_initialized){
            tinyMCE.init({
                mode: "none",
                theme: "simple"
            });
        }
    }
    var load_page = function(we, url){
        return we.dialog.load(url);
    };

    var on_dialog = function(we){
        _initialize()
        tinyMCE.execCommand("mceAddControl", true, "freetext_widget_textarea");
    };

    var on_selected = function(we){
        // tinyMCE.execCommand("mceAddControl", true, "freetext_widget_textarea");
        $(document).off("click", _has_click_event);
    };

    var collect_data = function(we, choiced_elt){
        return {text: $(choiced_elt).html()};
    };

    return widget.include("freetext", {
        on_dialog: on_dialog, 
        on_selected: on_selected, 
        collect_data: collect_data, 
        save_url: "/sample/api/save/widget"
    });
})(widget); 

