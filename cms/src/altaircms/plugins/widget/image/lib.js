if(!widget){
    throw "widget module is not found";
}

var AjaxScrollableAPIGateway = function(pk, fetch_url, seach_url){
    this.pk = pk; // null if opened dialog, first time.
    this.fetch_url = fetch_url;
    this.seach_url = seach_url;
};
AjaxScrollableAPIGateway.prototype.fetch = function(i){
    return $.ajax(this.fetch_url, {
        dataType: "html",
        type: "GET",
        url: this.fetch_url,
        data: {"page": i, "widget": this.pk}
    }); //dfd
};
AjaxScrollableAPIGateway.prototype.search = function(word,i){
    return $.get(this.search_url, {"search_word": word, "page": i, "widget": this.pk}) //dfd
};

var AjaxImageAreaManager = function(root){
    this.root = root;
};
AjaxImageAreaManager.prototype.bind = function(root){
    this.root = root;
};
AjaxImageAreaManager.prototype.getImageArea = function(i){
    return this.root.find("group #group_"+(i-1));
};
AjaxImageAreaManager.prototype.injectImages = function(i, html){
    return this.getImageArea(i).html(html);
};

var AjaxScrollableHandler = function(gateway, areaManager){
    this.root = null;
    this.scrollable = null;
    this.cache = {}; //{1: true, 2: true, ...}
    this.gateway = gateway;
    this.areaManager = areaManager;
};
AjaxScrollableHandler.prototype.fetchImages = function(){
    var i = this.getIndex();
    if(!this.cache[i]){
        var self = this;
        return this.gateway.fetch(i).done(function(html){
            self.areaManager.injectImages(i, html);
            self.cache[i] = true //hmm;
        });
    }
};
AjaxScrollableHandler.prototype.bind = function(root){
    this.root = root;
    this.scrollable = root.data("scrollable");
    this.scrollable.onSeek(this.fetchImages.bind(this));
    this.areaManager.bind(root);
};
AjaxScrollableHandler.prototype.getIndex = function(){
    return this.scrollable.getIndex();
};


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

                    // pagination
                    $(".navi").empty();
                    $(".browse").removeClass("disabled");

                    $(".scrollable").remove();
                    $("#tag_search_form").after("<div class='scrollable' style='width: 550px'></div>");
                    $(".scrollable").append("<div class='items'></div>");

                    for (var groupNo in assets_data){
                        $(".scrollable .items").append("<div class='group' id='group_" + groupNo + "'></div>");
                        for (var itemNo in assets_data[groupNo]) {

                            $("#group_" + groupNo).append("<div class='item'></div>");

                            var managed_class = "";
                            if (assets_data[groupNo][itemNo]['id'] == widget_asset_id) {managed_class = "class='managed'"}

                            var img_temp = "<img pk='<%= id %>' src='<%=thumbnail_path%>' alt='' " + managed_class + " />";
                            var p_temp = "<p>title:<%= title %> width:<%= width %> height:<%= height %></p>";
                            $("#group_" + groupNo + " .item:eq(" + itemNo + ")").append(_.template(img_temp, assets_data[groupNo][itemNo]));
                            $("#group_" + groupNo + " .item:eq(" + itemNo + ")").append(_.template(p_temp, assets_data[groupNo][itemNo]));
                        }
                    }
                    addClickEvent();
                    moveSelectedItem();
                }

                $('#imgtabs').tabs();

                $("#image_submit").click(function(){
                    if ($(we.dialog).find(".managed").length) {
                        we.finish_dialog(this);
                    } else {
                        if(window.confirm('画像が選択されていません。本当に閉じますか？')){
                            we.finish_dialog(this);
                        }
                    }
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
