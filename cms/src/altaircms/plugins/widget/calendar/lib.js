
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

        // jquery.ui
        $.datepicker.setDefaults( $.datepicker.regional[ "ja" ] );
        var dates = $( "#from_date, #to_date" ).datepicker({
          // defaultDate: "+1w",
          numberOfMonths: 1,
          changeMonth: true,
          /*onSelect: function( selectedDate ) {
            var option = this.id == "from_date" ? "minDate" : "maxDate",
              instance = $( this ).data( "datepicker" ),
              date = $.datepicker.parseDate(
                instance.settings.dateFormat ||
                $.datepicker._defaults.dateFormat,
                selectedDate, instance.settings );
            dates.not( this ).datepicker( "option", option, date );
          },*/ 
            dateFormat: "yy/mm/dd"
        });


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
    };

    var on_close = function(we){
    };

    var collect_data = function(we, choiced_elt){
        return {calendar_type: $("#calendar_type").val(), 
                from_date: $("#from_date").val(), 
                to_date: $("#to_date").val()
               };
    };

    return widget.include("calendar", {
        load_page: load_page, 
        on_dialog: on_dialog, 
        on_close: on_close, 
        collect_data: collect_data, 
    });
})(widget); 
