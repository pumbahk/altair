
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
        var url = "/api/widget/countdown/dialog";
        var params = {};
        if(!!pk){
            params["pk"] = pk;
        }
            url += "?" + $.param(params);
        return we.dialog.load(url);
    };

    var on_dialog = function(we){
        var bind_retry = function bind_retry(n, i, d){
            if (i > n){
                alert("error: broken widget. please reload")
            }
            var elt = $("#submit");            
            if(elt.length <=0){
                console.log(elt.length);
                setTimeout(function(){bind_retry(n, i+1, d)}, d);
            }else {
                elt.click(function(){we.finish_dialog(this);});
            }
        };
        bind_retry(15, 0, 50);
    };

    var on_close = function(we){
    };

    var collect_data = function(we, choiced_elt){
        var root = $(we.dialog)
        return {"kind": root.find("#kind").val()}
    };
    return widget.include("countdown", {
        load_page: load_page, 
        on_dialog: on_dialog, 
        on_close: on_close, 
        collect_data: collect_data, 
    });
})(widget); 
