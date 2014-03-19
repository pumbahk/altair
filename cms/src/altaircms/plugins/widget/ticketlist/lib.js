
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
                      function(elt){
                          var root = elt.parents(".box");
                          root.find("#target_performance_id").change(function(e){
                              var target = root.find("#target_salessegment_id").parent();
                              var url = "/api/widget/ticketlist/api/combobox/salessegment?target_performance_id="+$(e.currentTarget).val();
                              $.get(url).done(function(data){
                                  target.html(data);
                              });
                          })
                          elt.click(function(){we.finish_dialog(this);});}
                     )();
    };

    var on_close = function(we){
    };

    var collect_data = function(we, choiced_elt){
        var root = $(we.dialog)
        return {"display_type": root.find("#display_type").val(), 
                "target_performance_id": root.find("#target_performance_id").val(), 
                "target_salessegment_id": root.find("#target_salessegment_id").val(), 
                "show_label": root.find("#show_label:checked").val() && "1", 
                "show_seattype": root.find("#show_seattype:checked").val() && "1",
                "caption": root.find("#caption").val()}
    };
    return widget.include("ticketlist", {
        load_page: load_page, 
        on_dialog: on_dialog, 
        on_close: on_close, 
        collect_data: collect_data, 
    });
})(widget); 
