
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
    var _with_pk = function(we, url){
        var pk = we.get_pk(we.where);
        var params = {};
        if(!!pk){
            params["pk"] = pk;
        }
            url += "?" + $.param(params);
        return url;
    }

    var load_page = function(we){
        var url = "/api/widget/calendar/dialog";
        return we.dialog.load(_with_pk(we, url));
    };

    var _has_click_event = "#calendar_submit";

    var _draw_demo_api = function(we, type){
        var url = "/api/widget/calendar/dialog/demo/@type@".replace("@type@", type);
        $("#canpas").load(_with_pk(we, url), function(){
            // // jquery.ui
            // var dates = $( "#from_date, #to_date" ).datepicker({
            //     numberOfMonths: 1,
            //     changeMonth: true,
            //     dateFormat: "yy-mm-dd"
            // });
            /* jquery.tools
            $.tools.dateinput.localize("ja",  {
                months: "１月, ２月, ３月, ４月, ５月, ６月, ７月, ８月, ９月, １０月, １１月, １２月", 
                shortMonths:   '1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12',
                days:          '月, 火, 水, 木, 金, 土, 日', 
                shortDays:     '月, 火, 水, 木, 金, 土, 日'
            });

            $("#from_date, #to_date").dateinput({ 
                lang: 'ja', 
                format: 'yyyy/mmmmm/dd',
                offset: [30, 0]
            });
            */
        });
    };

    var on_dialog = function(we){
        we.bind_retry(we, 10, 1.43, 15, 
                      function(){return $("#calendar_submit")}, 
                      function(elt){
                          $("#calendar_type").bind("change", function(){_draw_demo_api(we, $(this).val())});
                          _draw_demo_api(we, $("#calendar_type").val());
                          elt.click(function(){we.finish_dialog(this);});
                      }
                     )();
    };

    var on_close = function(we){
    };

    var collect_data = function(we, choiced_elt){
        return {calendar_type: $("#calendar_type").val(), 
                salessegment_id: $("#sale_choice").val()
//                from_date: $("#from_date").val(), 
                //to_date: $("#to_date").val()
               };
    };

    return widget.include("calendar", {
        load_page: load_page, 
        on_dialog: on_dialog, 
        on_close: on_close, 
        collect_data: collect_data, 
    });
})(widget); 
