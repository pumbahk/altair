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

                $(document).ready(function() {
                    $('#search_form').ajaxForm({dataType: 'json', success: successSearch});
                    $('#tag_search_form').ajaxForm({dataType: 'json', success: successSearch});
                });

                function successSearch(data) {
                    var assets_data = data.assets_data;
                    var widget_asset_id = data.widget_asset_id;

                    $(".scrollable").remove();
                    $(".navi").empty();
                    $("#image_tab").append("<div class='scrollable' style='width: 550px'></div>");
                    $(".scrollable").append("<div class='items'></div>");

                    for (var groupNo in assets_data){
                        $(".scrollable .items").append("<div class='group' id='group_" + groupNo + "'></div>");
                        for (var itemNo in assets_data[groupNo]) {
                            $("#group_" + groupNo).append("<div class='item'></div>");
                            var id = assets_data[groupNo][itemNo]['id'];
                            var title = assets_data[groupNo][itemNo]['title'];
                            var width = assets_data[groupNo][itemNo]['width'];
                            var height = assets_data[groupNo][itemNo]['height'];
                            var thumbnail_path = assets_data[groupNo][itemNo]['thumbnail_path'];
                            var managed_class = "";
                            if (id == widget_asset_id) {managed_class = "class='managed'"}
                            $("#group_" + groupNo + " .item:eq(" + itemNo + ")").append("<img pk='" + id + "' src='" + thumbnail_path + "' alt='' " + managed_class + " />");
                            $("#group_" + groupNo + " .item:eq(" + itemNo + ")").append("<p>title:" + title + "width:" + width + "height:" + height + "</p>");
                        }
                    }
                    addClickEvent();
                    moveSelectedItem();
                }

                $('#imgtabs').tabs();

                $("#image_submit").click(function(){
                    we.finish_dialog(this);
                })

                $("#image_info_submit").click(function(){
                    we.finish_dialog(this);
                })

                addClickEvent();
                moveSelectedItem();
            })();

        function addClickEvent() {
            $(we.dialog).find("img").click(function(){
                selected = this;
                $(we.dialog).find(".managed").removeClass("managed")
                we.attach_managed(selected);
            });
        }

        function moveSelectedItem() {
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
                var k = selected.parents(".group").eq(0).attr("id").split("_")[1];
                root.data("scrollable").move(k, 1);
            }
        }
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
