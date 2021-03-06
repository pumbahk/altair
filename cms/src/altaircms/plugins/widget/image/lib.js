if(!widget){
    throw "widget module is not found";
}

(function(widget){
    // utility
    var ChunkedApiWrapper = function(api, offset, chunkSize){
        this.cache = {};
        this.api = api;

        this.page_offset = offset;
        this.page_chunk_size = chunkSize;
        this.server_page_offset = this.page_offset * this.page_chunk_size;
    };
    ChunkedApiWrapper.prototype.clean = function(){
        this.cache = {};
    };
    ChunkedApiWrapper.prototype.realPageIndex = function(page){
        return Math.floor(page / this.page_chunk_size);
    };
    ChunkedApiWrapper.prototype.chunkIndex = function(page){
        return page % this.page_chunk_size;
    };
    ChunkedApiWrapper.prototype.dataFromCache = function(cached,i){
        var idx = this.page_offset * this.chunkIndex(i);
        //json :: {assets: [], widget: {}, "pk": 0}
        var assets = [];
        var data = {"widget": cached["widget"],
                    "assets": assets,
                    "pk": cached["pk"]
                   };
        var cached_assets = cached["assets"];
        for(var j=idx,k=idx+this.page_offset; j<k; j++){
            var v = cached_assets[j]
            if(!v){
                break;
            }
            assets.push(v);
        }
        return data;
    };
    ChunkedApiWrapper.prototype.callAPI = function(word, i){
        var page = this.realPageIndex(i);
        // console.log("*debug i: ", i,"realPageIndex: ",page);
        var cached = this.cache[page];
        //debug* window.PageCache = this.cache;
        var self = this;
        var dfd = new $.Deferred();
        if(!!cached){
            return dfd.resolve(this.dataFromCache(cached, i));
        }
        //debug* window.Chunked = this;
        this.api(word, page, this.server_page_offset).done(function(data){
            //debug* window.APIData = data;
            self.cache[page] = data;
            dfd.resolve(self.dataFromCache(data, i));
        });
        return dfd.promise();
    };

    var AjaxScrollableAPIGateway = function(pk, fetch_url, search_url, tag_search_url){
        this.pk = pk; // null if opened dialog, first time.
        this.fetch_url = fetch_url;
        this.search_url = search_url;
        this.tag_search_url = tag_search_url;
        this.needCleans = [];
    };
    AjaxScrollableAPIGateway.prototype.clean = function(){
        var cleans = this.needCleans;
        for(var i=0,j=cleans.length;i<j;i++){
            if(!!cleans[i].clean){
                // console.log("*debug clean: "+cleans[i]);
                cleans[i].clean(); //hmm.
            }
        }
    };
    AjaxScrollableAPIGateway.prototype.fetch = function(word, i, offset){
        var params = {"page": i, "pk": this.pk};
        if(!!offset){
            params["offset"] = offset;
        }
        return $.ajax(this.fetch_url, {
            dataType: "json",
            type: "GET",
            data: params
        }); //dfd
    };
    AjaxScrollableAPIGateway.prototype.search = function(word, i, offset){
        var params = {"page": i, "pk": this.pk, "search_word": word};
        if(!!offset){
            params["offset"] = offset;
        }
        return $.ajax(this.search_url, {
            dataType: "json",
            type: "GET",
            data: params
        }); //dfd
    };
    AjaxScrollableAPIGateway.prototype.tag_search = function(word, i, offset){
        var params = {"page": i, "pk": this.pk, "tags": word};
        if(!!offset){
            params["offset"] = offset;
        }
        return $.ajax(this.tag_search_url, {
            dataType: "json",
            type: "GET",
            data: params
        }); //dfd
    };

    var AjaxImageAreaManager = function(root){
        this.we = null;
        this.root = root;
    };
    AjaxImageAreaManager.prototype.bind = function(we, root){
        this.we = we;
        this.root = root;
        this.highlightImage(root.find(".managed"));
        this.root.on("click", ".group img" ,function(e){this.selectImage($(e.currentTarget));}.bind(this));
    };
    AjaxImageAreaManager.prototype.getImageArea = function(i){
        return this.root.find(":not(.cloned).group#group_"+(i));
    };
    var ItemsDivTemplate = _.template([
        '<% _.each(data.assets, function(asset) { %>',
        '<div class="item<%= asset.class %>">',
        '<img pk="<%- asset.id%>" src="<%- asset.thumbnail_src %>" <%= asset.managed %>/>',
        '<p class="title"><%- asset.title %></p>',
        '<p><span class="item-width"><%- asset.width %></span>x<span class="item-height"><%- asset.height %></span></p>',
        '<p><%- asset.updated_at %></p>',
        '</div>',
        '<% }); %>'
    ].join("\n"));
    ItemsDivTemplate.buildVars = function(data){
        var assets = data.assets;
        var asset_id = data.widget.asset_id;
        for(var i=0,j=assets.length; i<j; i++){
            assets[i].class = "";
            assets[i].managed = assets[i].id === asset_id ? 'class="managed"' : '';
        }
        if(!!assets[0]){
            assets[0].class = " first";
        }
        if(!!assets[assets.length-1]){
            assets[assets.length-1].class = " last";
        }
        return data;
    }; //xxx:
    AjaxImageAreaManager.prototype.updatePagination = function(i){
        this.root.find(".page-navi .js-page-current").text(i);
    };
    AjaxImageAreaManager.prototype.injectImages = function(i, data){
        // need model?
        var data = ItemsDivTemplate.buildVars(data);
        var html = ItemsDivTemplate({data: data});
        // console.log("*debug area="+this.getImageArea(i));
        // console.log("*debug area length="+this.getImageArea(i).length);
        var e = this.getImageArea(i).html(html);
        this.highlightImage(this.root.find(".managed"));
        return e;
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
        this.gateway = gateway;
        this.areaManager = areaManager;
        this.apiType = "fetch"; // fetch or search or tag_search
        this.word = "" // search word
        this.semaphore = {fetch: {}, search: {}, tag_search: {}}
    };
    AjaxScrollableHandler.prototype.setSearchWord = function(apiType, word){
        // console.log("*debug setword: "+word);
        this.apiType = apiType;
        this.word = word;
    };
    AjaxScrollableHandler.prototype.fetchImages = function(){
        var i = this.getIndex();
        var apiType = this.apiType;
        // console.log("*debug fetch images i="+i+" cached="+this.semaphore[apiType][i])
        if(i >= 0){
            if(!this.semaphore[apiType][i]){
                this.semaphore[apiType][i] = true //hmm;
                var self = this;
                // notice: ducktyping.
                return this.gateway[apiType](this.word, i).done(function(data){
                    // console.log("*debug api="+apiType+" word="+this.word+" i="+i+" data="+JSON.stringify(data));
                    self.areaManager.injectImages(i, data);
                    self.areaManager.updatePagination(i);
                });
            } else {
                this.areaManager.updatePagination(i);
            }
        }
    };
    AjaxScrollableHandler.prototype.bind = function(root){
        var $scrollable = root.find(".scrollable");
        this.root = $scrollable;
        this.areaManager.bind(this.we, $scrollable);
    };
    AjaxScrollableHandler.prototype.setupScrollable = function($scrollable){
        // after call setupScrollable of SearchHandler
        this.scrollable = $scrollable.data("scrollable");
        this.scrollable.onSeek(this.fetchImages.bind(this));
        this.semaphore = {fetch: {}, search: {}, tag_search: {}};
        this.gateway.clean();
    };
    AjaxScrollableHandler.prototype.getIndex = function(){
        return this.scrollable.getIndex();
    };

    //
    var SearchHandler = function(we, areaManager){
        this.root = null;
        this.we = we;
        this.areaManager = areaManager;
        this.afterSearchSubmitHook = function(){alert("invalid search hook")}; //todo: observer
        this.afterScrollableSetupHook = function(){alert("invalid setup hook")}; //todo: observer
    };

    SearchHandler.prototype.bind = function(root, search_form, tag_search_form){
        this.root = root;
        this.areaManager.bind(root);
        this.setupScrollable(this.areaManager.$scrollable);

        var onSuccess = this.afterSearch.bind(this);
        var onFailure = (function(){alert(data);});
        var self = this;
        // todo: add failure cont.
        $('#search_form').ajaxForm({dataType: 'json', success: onSuccess, failure: onFailure,
                                    timeout: 1000,
                                    beforeSubmit: function(arr, $form, options){
                                        for(var i=0,j=arr.length;i<j;i++){
                                            if(arr[i].name == "search_word"){
                                                self.afterSearchSubmitHook("search", arr[i].value);
                                            }
                                        }
                                        //console.log(arr);
                                        return true;
                                    }});
        $('#tag_search_form').ajaxForm({dataType: 'json', success: onSuccess, failure: onFailure,
                                        timeout: 1000,
                                        beforeSubmit: function(arr, $form, options){
                                            for(var i=0,j=arr.length;i<j;i++){
                                                if(arr[i].name == "tags"){
                                                    self.afterSearchSubmitHook("tag_search", arr[i].value);
                                                }
                                            }
                                            //console.log(arr);
                                            return true;
                                        }});
    };
    SearchHandler.prototype.setupScrollable = function($scrollable){
        // **scroiing**
        // horizontal scrollables. each one is circular and has its own navigator instance
        $scrollable.scrollable({circular: true, keyboard: true});
        $scrollable.navigator(".navi").eq(0).data("scrollable").focus();

        var move = $scrollable.data("scrollable").move;
        this.root.parent().mousewheel(function(e, delta){
            move((isNaN(delta) ? 1 : delta < 0 ? 1 : -1), 0.1); // 0.1 is speed
            return false;
        });
        // console.log("*debug setup scrollable");
        this.afterScrollableSetupHook($scrollable);
    };
    SearchHandler.prototype.destroyScrollable = function($scrollable){
        // console.log("*debug destroy scrollable");
        var scrollableJQObject = $($scrollable.data("scrollable"));
        var events = ['onBeforeSeek', 'onSeek', 'onAddItem'];
        for(var i=0,j=events.length; i<j; i++){
            scrollableJQObject.off(events[i]);
        }
        delete scrollableJQObject;
        $scrollable.data("scrollable",null);
    };
    SearchHandler.prototype.afterSearch = function(data){
        this.areaManager.redraw(data);
        this.destroyScrollable(this.areaManager.$scrollable);
        this.setupScrollable(this.areaManager.$scrollable);
    }
    var SearchAreaManager = function(root){
        this.root = root; //$el?
        this.$navi = null;
        this.$browse = null;
        this.$scrollable = null;
    };
    SearchAreaManager.prototype.bind = function(root){
        this.root = root;
        this.$navi = root.find(".navi");
        this.$browse = root.find(".browse");
        this.$scrollable = root.find(".scrollable");
        if(!this.$navi.length){
            throw ".navi is not found";
        }
        if(!this.$browse.length){
            throw ".browse is not found";
        }
        if(!this.$scrollable.length){
            throw ".scrollable is not found";
        }
    };
    var DrawableTemplate = _.template([
        '<p class="page-navi"><span class="js-page-current">0</span>/<span class="js-page-max"><%- (data.max_of_pages-1) %></span></p>',
        '<div class="items">',
        '<% _.times(data.max_of_pages, function(i) { %>',
        '<div class="group" id="group_<%- i %>">',
        '<% if (i==0) {%>',
        '<%= firstItemContent %>',
        '<% } %>',
        '</div>',
        '<% }); %>',
        '</div>'
    ].join("\n"));
    SearchAreaManager.prototype.redraw = function(data){
        //before
        this.$navi.empty();
        this.$browse.removeClass("disabled");
        //redraw
        var content = ItemsDivTemplate({"data": ItemsDivTemplate.buildVars(data)});
        this.$scrollable.html(DrawableTemplate({"data": data, "firstItemContent": content}));
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
    }

    ApplicationHandler.prototype.choicedElement = function(){
        return this.submitHandler.$choicedElement;
    };

    var setupApplicationHandler = function(we, gateway){
        var scrollableHandler = new AjaxScrollableHandler(we, gateway, new AjaxImageAreaManager());
        var searchHandler = new SearchHandler(we, new SearchAreaManager()); //hmm.
        var submitHandler = new SubmitHandler(we);
        var tabHandler = new TabHandler(we, "image");

        // setting hook. todo: list?
        searchHandler.afterSearchSubmitHook = scrollableHandler.setSearchWord.bind(scrollableHandler);
        searchHandler.afterScrollableSetupHook = scrollableHandler.setupScrollable.bind(scrollableHandler);
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
    ///


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
            var setUpWrapper = function(gateway, action){
                var PageOffset = 5;
                var PageChunkSize = 6;
                var wrapper = new ChunkedApiWrapper(gateway[action].bind(gateway), PageOffset, PageChunkSize)
                gateway.needCleans.push(wrapper);
                return wrapper.callAPI.bind(wrapper);
            };
            var chunkedAPIGateway = Object.create(gateway, {
                    gateway: {value: gateway},
                    fetch: {value: setUpWrapper(gateway, "fetch")},
                    search: {value: setUpWrapper(gateway, "search")},
                    tag_search: {value: setUpWrapper(gateway, "tag_search")}
            });

            appHandler = setupApplicationHandler(we, chunkedAPIGateway);
            widget.env.image.appHandler = appHandler; // for debug;
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
                align: root.find("#align").val() || "",
                disable_right_click: root.find("#disable_right_click").attr("checked")
               };
    };

    return widget.include("image", {
        load_page: load_page,
        on_dialog: on_dialog,
        on_close: on_close,
        collect_data: collect_data,
    });
})(widget);
