
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
        var url = "/api/widget/ticketlist/dialog";
        var params = {"page_id": get_page()}; //get_page is global function. it isnt good idea
        if(!!pk){
            params["pk"] = pk;
        }
        url += "?" + $.param(params);
        return we.dialog.load(url);
    };
    var on_dialog = function(we){
        we.bind_retry(we, 10, 1.43, 15, 
                      function(){return $("#ticketlist_submit")}, 
                      function(elt){elt.click(function(){we.finish_dialog(this);});}
                     )();
    };

    var on_close = function(we){
    };

    var collect_data = function(we, choiced_elt){
        var root = $(we.dialog)
        return {"kind": root.find("#kind").val(), 
                "target_performance_id": root.find("#target").val(), 
                "caption": root.find("#caption").val()}
    };
    return widget.include("ticketlist", {
        load_page: load_page, 
        on_dialog: on_dialog, 
        on_close: on_close, 
        collect_data: collect_data, 
    });
})(widget); 
