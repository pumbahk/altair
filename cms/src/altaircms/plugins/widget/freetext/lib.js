if(!widget){
    throw "widget module is not found";
}

(function(widget){
    var _has_click_event = "#submit";
    var is_initialized = false;

    var _initialize = function(we){
        if(!is_initialized){
            tinyMCE.init({
                mode: "none",
                // theme: "simple", 
                theme: "advanced", 
                dialog_type: "modal", 
                theme_advanced_font_sizes : "10px,12px,14px,16px,24px", 
                valid_elements : "a[href|target=_blank],strong/b,div[align],br,h1[class|style],h2[class|style],h3[class|style],h4[class|style],h5[class|style]"
            });
            is_initialized = true;
        }
    }
    var load_page = function(we){
        var pk = we.get_pk(we.where);
        var url = "/api/widget/freetext/dialog";
        var params = {};
        if(!!pk){
            params["Pk"] = pk;
        }
            url += "?" + $.param(params);
        return we.dialog.load(url);
    };
    var on_dialog = function(we){
        _initialize(we)
        tinyMCE.execCommand("mceAddControl", true, "freetext_widget_textarea");
        var freetext = we.get_data(we.where).freetext;            
        if(!!freetext){
            setTimeout(function(){ //fixme
                tinyMCE.get("freetext_widget_textarea").setContent(freetext);
            }, 200);
        }
        $(document).on("click", _has_click_event, function(){
            we.finish_dialog(this);
        });
    };

    var on_close = function(we){
        tinyMCE.execCommand("mceRemoveControl", true, "freetext_widget_textarea");
        $(document).off("click", _has_click_event);
    };

    var collect_data = function(we, choiced_elt){
        return {freetext: tinyMCE.get("freetext_widget_textarea").getContent()};
    };

    return widget.include("freetext", {
        load_page: load_page, 
        on_dialog: on_dialog, 
        on_close: on_close, 
        collect_data: collect_data, 
    });
})(widget); 

