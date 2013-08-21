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
        we.bind_retry(we, 
            10, 1.43, 15, 
            function(){return $(".scrollable")}, 
            function(){
                $("#image_submit").click(function(){
                    if ($(we.dialog).find(".managed").length) {
                        we.finish_dialog(this);
                    } else {
                        if(window.confirm('画像が選択されていません。本当に閉じますか？')){
                            we.finish_dialog(this);
                        }
                    }
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
                    move(delta < 0 ? 1 : -1, 40); // 50 is speed
                    return false;
                });
                if(!!selected.length > 0){
                    var k = selected.parents(".group").eq(0).attr("id").split(":")[1];
                    root.data("scrollable").move(k, 1);
                }
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
                align: root.find("#align").val() || ""
               };
    };

    return widget.include("image", {
        load_page: load_page, 
        on_dialog: on_dialog, 
        on_close: on_close, 
        collect_data: collect_data, 
    });
})(widget); 
