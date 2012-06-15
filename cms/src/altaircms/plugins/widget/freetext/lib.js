if(!widget){
    throw "widget module is not found";
}

(function(widget){
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
            params["pk"] = pk;
        }
            url += "?" + $.param(params);
        return we.dialog.load(url);
    };
    var on_dialog = function(we){
        setTimeout(function(){ //todo refactoring
            we.bind_retry(we, 10, 1.43, 15, 
                      function(){return $("#freetext_widget_textarea")}, 
                      function(elt){
                          _initialize(we)
                          tinyMCE.execCommand("mceAddControl", true, "freetext_widget_textarea");
                          var freetext = we.get_data(we.where).freetext;            
                          if(!!freetext){ //fixme
                              setTimeout(function(){ //fixme
                                  tinyMCE.get("freetext_widget_textarea").setContent(freetext);
                              }, 20);
                          }
                          $("#freetext_submit").click(function(){we.finish_dialog(this);});
                      }
                     )();
        }, 200);
    };

    var on_close = function(we){
        tinyMCE.execCommand("mceRemoveControl", true, "freetext_widget_textarea");
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

