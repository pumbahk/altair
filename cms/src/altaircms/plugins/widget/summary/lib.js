
if(!widget){
    throw "widget module is not found";
}

/* we argument has
widget.configure({
    dialog: null, //dynamic bind
    widget_name: null, //dynamic bind
    where: null, //dynamic bind
    get_pk: function(e){
    }, 
    get_data: function(e){
    }, 
    set_data: function(e, data){
    }, 
    attach_highlight: function(e){
    }, 
    attach_managed: function(e){
    }, 
    get_display_order: function(e){
    }
});
*/

(function(widget){
    var opt = {} //widget local variable
    var load_page = function(we){
        var pk = we.get_pk(we.where);
        var params={page: get_page()};
        var url = "/api/widget/summary/dialog";
        if(!!pk){
            params["pk"] = pk
        }
        url += "?" + $.param(params);
        return we.dialog.load(url);
    };

    var on_dialog = function(we){
        we.bind_retry(we, 10, 1.43, 15, 
                      function(){return $("#summary_submit")}, 
                      function(elt){elt.click(function(){we.finish_dialog(this);});}
                     )();
    };

    var on_close = function(we){
    };

    var collect_data = function(we, choiced_elt){
        return {"items": JSON.stringify($("#app").data("appview").collectData()), 
                "show_label": !!($(we.dialog).find("#show_label").attr("checked")), 
                "use_notify": !!($(we.dialog).find("#use_notify").attr("checked"))};
    };
    return widget.include("summary", {
        load_page: load_page, 
        on_dialog: on_dialog, 
        on_close: on_close, 
        collect_data: collect_data, 
    });
})(widget); 
