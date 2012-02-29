
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
        we.dialog.load("/api/widget/calendar/dialog");
    };

    var on_dialog = function(we){
        $("#calendar_type").live("change", function(){
            var type = $(this).val();
            var url = "/api/widget/calendar/dialog/demo/@type@".replace("@type@", type);
            console.log(url);
            // $("#canpas").load(url);
        });
    };

    var on_close = function(we){
    };

    var collect_data = function(we, choiced_elt){
    };
    return widget.include("calendar", {
        load_page: load_page, 
        on_dialog: on_dialog, 
        on_close: on_close, 
        collect_data: collect_data, 
    });
})(widget); 
