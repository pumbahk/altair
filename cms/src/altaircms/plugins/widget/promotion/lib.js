
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
        var url = "/api/widget/promotion/dialog";
        var params = {}
        if(!!pk){
            params["pk"] = pk;
        }
        params["page"] = get_page();
        url += "?" + $.param(params);   
        return we.dialog.load(url);
    };

    var on_dialog = function(we){
        we.bind_retry(we, 10, 1.43, 15, 
                      function(){return $("#promotion_submit")}, 
                      function(elt){elt.click(function(){we.finish_dialog(this);});}
                     )();
    };

    var on_close = function(we){
    };

    var collect_data = function(we, choiced_elt){
        var root = $(we.dialog);
        return {"display_type": root.find("#display_type").val(), 
                "tag": root.find("#tag").val(), 
                "system_tag": root.find("#system_tag").val(),
                "use_newstyle": root.find("#use_newstyle").attr("checked")};
    };
    return widget.include("promotion", {
        load_page: load_page, 
        on_dialog: on_dialog, 
        on_close: on_close, 
        collect_data: collect_data, 
    });
})(widget); 
