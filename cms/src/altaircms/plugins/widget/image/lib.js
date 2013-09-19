if(!widget){
    throw "widget module is not found";
}

var AjaxScrollableAPIGateway = function(pk, fetch_url, search_url, tag_search_url){
    this.pk = pk; // null if opened dialog, first time.
    this.fetch_url = fetch_url;
    this.search_url = search_url;
    this.tag_search_url = tag_search_url;
};
AjaxScrollableAPIGateway.prototype.fetch = function(word, i){
    return $.ajax(this.fetch_url, {
        dataType: "html",
        type: "GET",
        data: {"page": i, "widget": this.pk}
    }); //dfd
};
AjaxScrollableAPIGateway.prototype.search = function(word, i){
    return $.ajax(this.search_url, {
        dataType: "html",
        type: "GET",
        data: {"page": i, "widget": this.pk, "search_word": word}
    }); //dfd
};
AjaxScrollableAPIGateway.prototype.tag_search = function(word, i){
    return $.ajax(this.tag_search_url, {
        dataType: "html",
        type: "GET",
        data: {"page": i, "widget": this.pk, "tags": word}
    }); //dfd
};

var AjaxImageAreaManager = function(root){
    this.we = null;
    this.root = root;
};
AjaxImageAreaManager.prototype.bind = function(we, root){
    this.we = we;
    this.root = root;
    var $dialog = $(we.dialog);
    this.highlightImage($dialog.find(".managed"));
    this.root.on("click", ".group img" ,function(e){this.selectImage($(e.currentTarget));}.bind(this));
};
AjaxImageAreaManager.prototype.getImageArea = function(i){
    return this.root.find(".group#group_"+(i-1));
};
AjaxImageAreaManager.prototype.injectImages = function(i, html){
    return this.getImageArea(i).html(html);
};
AjaxImageAreaManager.prototype.selectImage = function(selected){
    var we = this.we;
    $(we.dialog).find(".managed").removeClass("managed");
    we.attach_managed(selected);
};
AjaxImageAreaManager.prototype.highlightImage = function(selected){
    var we = this.we;
    we.attach_managed(selected);
};

var AjaxScrollableHandler = function(we, gateway, areaManager){
    this.we = we;
    this.root = null;
    this.scrollable = null;
    this.cache = {fetch: {}, search: {}}; //{1: true, 2: true, ...}
    this.gateway = gateway;
    this.areaManager = areaManager;
    this.apiType = "fetch"; // fetch or search or tag_search
    this.word = "" // search word
};
AjaxScrollableHandler.prototype.setSearchWord = function(apiType, word){
    //console.log(word);
    this.apiType = apiType;
    this.word = word;
};
AjaxScrollableHandler.prototype.fetchImages = function(){
    var i = this.getIndex();
    var apiType = this.apiType;
    if(!this.cache[apiType][i]){
        this.cache[apiType][i] = true //hmm;
        var self = this;
        // notice: ducktyping.
        return this.gateway[apiType](this.word, i).done(function(html){
            self.areaManager.injectImages(i, html);
        });
    }
};
AjaxScrollableHandler.prototype.bind = function(root){
    var $scrollable = root.find(".scrollable");
    this.root = $scrollable;
    this.scrollable = $scrollable.data("scrollable");
    this.scrollable.onSeek(this.fetchImages.bind(this));
    this.areaManager.bind(this.we, $scrollable);
};
AjaxScrollableHandler.prototype.getIndex = function(){
    return this.scrollable.getIndex();
};

//
var SearchHandler = function(we, areaManager){
    this.root = null;
    this.we = we;
    this.areaManager = areaManager;
    this.afterSearchSubmitHook = function(){}; //todo: observer
};

SearchHandler.prototype.bind = function(root, search_form, tag_search_form){
    this.root = root;
    this.areaManager.bind(root);
    var successSearch = this.afterSearch.bind(this);
    var self = this;
    // todo: add failure cont.
    $('#search_form').ajaxForm({dataType: 'json', success: successSearch,
                               beforeSubmit: function(arr, $form, options){
                                   for(var i=0,j=arr.length;i<j;i++){
                                       if(arr[i].name == "search_word"){
                                           self.afterSearchSubmitHook("search", arr[i].value);
                                       }
                                   }
                               }});
    $('#tag_search_form').ajaxForm({dataType: 'json', success: successSearch,
                               beforeSubmit: function(arr, $form, options){
                                   for(var i=0,j=arr.length;i<j;i++){
                                       if(arr[i].name == "tags"){
                                           self.afterSearchSubmitHook("tag_search", arr[i].value);
                                       }
                                   }
                               }});
};
SearchHandler.prototype.afterSearch = function(data){
    var assets_data = data.assets_data;
    var widget_asset_id = data.widget_asset_id;
    
    this.areaManager.redraw(assets_data,widget_asset_id);
    addClickEvent();
    moveSelectedItem();
}

var SearchAreaManager = function(root){
    this.root = root; //$el?
};
SearchAreaManager.prototype.bind = function(root){
    this.root = root;
}
SearchAreaManager.prototype.redraw = function(assets_data, widget_asset_id){
    // pagination
    $(".navi").empty();
    $(".browse").removeClass("disabled");

    $(".scrollable").remove();
    //$("#tag_search_form").after("<div class='scrollable' style='width: 550px'></div>");
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
};

var SubmitHandler = function(we){
    this.we = we;
    this.root = null;
    this.submitBtn = null; //for debug
    this.infoSubmitBtn = null; //for debug
    this.$submitBtn = null;
    this.$infoSubmitBtn = null;
}
SubmitHandler.prototype.bind = function(root, submitBtn, infoSubmitBtn){
    this.root = root;
    this.submitBtn = submitBtn;
    this.infoSubmitBtn = infoSubmitBtn;
    this.$submitBtn = this.root.find(submitBtn);
    this.$infoSubmitBtn = this.root.find(infoSubmitBtn);
    this.$submitBtn.click(this.afterSubmit.bind(this));
    this.$infoSubmitBtn.click(this.justFinish.bind(this));
    this.$choicedElement = null;
};
SubmitHandler.prototype.justFinish = function(){
    we = this.we;
    this.$choicedElement = this.root.find(".managed");
    we.finish_dialog(this);
}
SubmitHandler.prototype.afterSubmit = function(){
    if (this.root.find(".managed").length) {
        this.justFinish();
    } else {
        if(window.confirm('画像が選択されていません。本当に閉じますか？')){
            this.justFinish();
        }
    }
}

var ApplicationHandler = function(we, scrollableHandler, searchHandler, submitHandler, tabHandler){
    this.we = we;
    this.scrollableHandler = scrollableHandler;
    this.searchHandler = searchHandler;
    this.submitHandler = submitHandler;
    this.tabHandler = tabHandler;
};

ApplicationHandler.prototype.bind = function(root, submitBtn, infoSubmitBtn){
    this.scrollableHandler.bind(root);
    this.searchHandler.bind(root);
    this.submitHandler.bind(root, submitBtn, infoSubmitBtn);
    this.tabHandler.bind(root);
    
    // setting hook. todo: list?
    this.searchHandler.afterSearchSubmitHook = this.scrollableHandler.setSearchWord.bind(this.scrollableHandler);
}

ApplicationHandler.prototype.choicedElement = function(){
    return this.submitHandler.$choicedElement;
};

var setupApplicationHandler = function(we, gateway){
    var scrollableHandler = new AjaxScrollableHandler(we, gateway, new AjaxImageAreaManager());
    var searchHandler = new SearchHandler(we, new SearchAreaManager()); //hmm.
    var submitHandler = new SubmitHandler(we);
    var tabHandler = new TabHandler(we, "image");
    return new ApplicationHandler(we, scrollableHandler, searchHandler, submitHandler, tabHandler);
};

/// tab handler
var TabHandler = function TabHandler(we,current){
    this.we = we;
    this.$el = null;
    this.current = current;
};
TabHandler.prototype.bind = function(root){
    var self = this;
    this.root = root;
    this.root.find("#image_ref").on("click", function(){self.next("image");});
    this.root.find("#setting_ref").on("click", function(){self.next("setting");});
};
TabHandler.prototype.on_image_input = function(){
  if("image" === this.current){
     return;
  }
  this.root.find("#setting_tab").hide();
  this.root.find("#image_tab").show();
  this.root.find("#image_ref").tab("show");
};
TabHandler.prototype.on_setting_input = function(){
  if("setting" === this.current){
     return;
  }
  this.root.find("#image_tab").hide();
  this.root.find("#setting_tab").show();
  this.root.find("#setting_ref").tab("show")
};
TabHandler.prototype.next = function(target){
  switch(target){
    case "image":
      this.on_image_input(); break;
    case "setting":
      this.on_setting_input(); break;
  }
  this.current = target;
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

    var appHandler = null; //hmm..

    var on_dialog = function(we){
        we.bind_retry(we, 
          10, 1.43, 15, 
          function(){return $(".scrollable")}, 
          function(){
            var gateway = new AjaxScrollableAPIGateway(
                we.get_pk(we.where),
                "/api/widget/image/fetch",
                "/api/widget/image/search",
                "/api/widget/image/tag_search"
            );
            appHandler = setupApplicationHandler(we, gateway);
            widget.env.image.appHandler = appHandler; // for debug;
            // **scroiing**
            // horizontal scrollables. each one is circular and has its own navigator instance
            var root = $(".scrollable").scrollable({circular: true, keyboard: true});
            root.navigator(".navi").eq(0).data("scrollable").focus();

            var move = root.data("scrollable").move;
            $(we.dialog).parent().mousewheel(function(e, delta){
                move(delta < 0 ? 1 : -1, 40); // 50 is speed
                return false;
            });

            appHandler.bind($(we.dialog), "#image_submit", "#image_info_submit");
            // if(!!selected.length > 0){
            //     var k = selected.parents(".group").eq(0).attr("id").split("_")[1];
            //     root.data("scrollable").move(k, 1);
            // }

          })();

    };

    var on_close = function(we){
    };

    var collect_data = function(we, choiced_elt){
        var choiced_elt = appHandler.choicedElement(); // module global variable
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
