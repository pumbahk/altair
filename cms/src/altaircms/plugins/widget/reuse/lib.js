
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
    get_orderno: function(e){
    }
});
*/

(function(widget){
    var opt = {} //widget local variable
    var load_page = function(we){
        var pk = we.get_pk(we.where);
        var url = "/api/widget/reuse/dialog";
        var params = {};
        if(!!pk){
            params["pk"] = pk;
        }
        url += "?" + $.param(params);
        return we.dialog.load(url);
    };

    var on_dialog = function(we){
        we.bind_retry(15, 25, 
                      function(){return $("#submit")}, 
                      function(elt){elt.click(function(){we.finish_dialog(this);});}
                     )();
    };

    var on_close = function(we){
    };

    var collect_data = function(we, choiced_elt){
        var root = $(we.dialog);
        return {"source_page_id": root.find("#source_page_input").val(), 
                "width": root.find("#width_input").val(), 
                "height": root.find("#height_input").val()
               };
    };
    return widget.include("reuse", {
        load_page: load_page, 
        on_dialog: on_dialog, 
        on_close: on_close, 
        collect_data: collect_data, 
    });
})(widget); 
