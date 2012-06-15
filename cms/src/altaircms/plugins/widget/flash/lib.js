
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
    var _has_click_event = null;

    var load_page = function(we){
        we.dialog.load("/api/widget/flash/dialog");
    };

    var on_dialog = function(we){
        we.bind_retry(
            10, 1.43, 15, 
            function(){return $(".scrollable")}, 
            function(){

                _has_click_event = "#@id@ img".replace("@id@", we.dialog .attr("id"));
                $(document).on("click", _has_click_event, function(){
                    we.finish_dialog(this);
                });
                we.attach_highlight(_has_click_event);
                var expr = "img[src='@src@']".replace("@src@", we.get_data(we.where).imagefile)
                we.attach_managed(we.dialog.find(expr));

                // **scroiing**
                // horizontal scrollables. each one is circular and has its own navigator instance
                var root = $(".scrollable").scrollable({circular: true, keyboard: true});
                root.navigator(".navi").eq(0).data("scrollable").focus();
                var move = root.data("scrollable").move;
                $(we.dialog).parent().mousewheel(function(e, delta){
                    move(delta < 0 ? 1 : -1, 50); // 50 is speed
					          return false;
                });
                // when page loads setup keyboard focus on the first horzontal scrollable
            })();
    };

    var on_close = function(we){
        $(document).off("click", _has_click_event);
    };

    var collect_data = function(we, choiced_elt){
        var choiced_elt = $(choiced_elt);
        return {imagefile: choiced_elt.attr("src"), 
                asset_id: choiced_elt.attr("pk")};

    };
    return widget.include("flash", {
        load_page: load_page, 
        on_dialog: on_dialog, 
        on_close: on_close, 
        collect_data: collect_data, 
    });
})(widget); 
