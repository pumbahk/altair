
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
        var url = "/api/widget/menu/dialog";
        var params = {"page": get_page()};
        if(!!pk){
            params["pk"]  = pk;
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
        // read dialog.mako
        return {"items": JSON.stringify($("#app").data("appview").collectData())};
    };

    return widget.include("menu", {
        load_page: load_page, 
        on_dialog: on_dialog, 
        on_close: on_close, 
        collect_data: collect_data, 
    });
})(widget); 
