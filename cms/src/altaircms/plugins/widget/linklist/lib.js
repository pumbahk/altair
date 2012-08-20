
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
        var url = "/api/widget/linklist/dialog";
        var params = {}
        if(!!pk){
            params["pk"] = pk;
        }
        url += "?" + $.param({"pk": pk});   
        return we.dialog.load(url);
    };

    var on_dialog = function(we){
        we.bind_retry(we, 10, 1.43, 15, 
                      function(){return $("#linklist_submit")}, 
                      function(elt){elt.click(function(){we.finish_dialog(this);});}
                     )();
    };

    var on_close = function(we){
    };

    var collect_data = function(we, choiced_elt){
        var root = $(we.dialog);
        return {"finder_kind": root.find("#finder_kind").val(), 
                "max_items": root.find("#max_items").val(), 
                "limit_span": root.find("#limit_span").val(), 
                "delimiter": root.find("#delimiter").val(), 
                "genre": root.find("#genre").val()
               };
    };
    return widget.include("linklist", {
        load_page: load_page, 
        on_dialog: on_dialog, 
        on_close: on_close, 
        collect_data: collect_data, 
    });
})(widget); 
