if(!widget){
    throw "widget module is not found";
}

(function(widget){
    var opt = {} //widget local variable

    var load_page = function(we){
        var pk = we.get_pk(we.where);
        var url = "/api/widget/image/dialog";
        var params = {};
        if(!!pk){
            params["pk"] = pk;
        }
            url += "?" + $.param(params);
        return we.dialog.load(url);
    };

    var selected = null;

    var on_dialog = function(we){
        we.bind_retry(
            10, 1.43, 15, 
            function(){return $(".scrollable")}, 
            function(){
                $("#image_submit").click(function(){
                    we.finish_dialog(this);
                })

                $(we.dialog).find("img").click(function(){
                    selected = this;
                    $(we.dialog).find(".managed").removeClass("managed")
                    we.attach_managed(selected);
                });

                selected = $(we.dialog).find(".managed");
                we.attach_highlight(selected);

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
    };

    var collect_data = function(we, choiced_elt){
        var choiced_elt = $(selected); // module global variable
        var root = $(we.dialog);
        return {imagefile: choiced_elt.attr("src"), 
                asset_id: choiced_elt.attr("pk"), 
                href: root.find("#href").val() || "", 
                width: root.find("#width").val() || "", 
                height: root.find("#height").val() || "", 
                alt: root.find("#alt").val() || "", 
               };
    };

    return widget.include("image", {
        load_page: load_page, 
        on_dialog: on_dialog, 
        on_close: on_close, 
        collect_data: collect_data, 
    });
})(widget); 
