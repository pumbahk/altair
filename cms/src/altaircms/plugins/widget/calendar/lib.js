
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
        var url = "/api/widget/calendar/dialog";
        if(!!pk){
            url += "?" + $.param({"pk": pk});
        }
        return we.dialog.load(url);
    };

    var _has_click_event = "#submit";

    var _draw_demo_api = function(type){
        var url = "/api/widget/calendar/dialog/demo/@type@".replace("@type@", type);
        $("#canpas").load(url);
    };

    var on_dialog = function(we){
        $(document).on("change", "#calendar_type", function(){
            _draw_demo_api($(this).val());
        });
        _draw_demo_api($("#calendar_type").val());
        $(document).on("click", _has_click_event, function(){
            we.finish_dialog(this);
        });
    };

    var on_close = function(we){
    };

    var collect_data = function(we, choiced_elt){
        return {calendar_type: $("#calendar_type").val()};
    };

    return widget.include("calendar", {
        load_page: load_page, 
        on_dialog: on_dialog, 
        on_close: on_close, 
        collect_data: collect_data, 
    });
})(widget); 
