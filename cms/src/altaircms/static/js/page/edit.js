// @require backbone.js
// @require jquery.js
// @require jquery-ui.js (draggble, droppable)
// @require jquery-tools (overlay)
// @require ./backbone_patch.js

var ApiUrlMapping = {
    BlockSheet: "/api/structure", 
    Widget: "/api/widget"
};

widget.configure({
    dialog: null, //dynamic bind
    widget_name: null, //dynamic bind
    where: null, //dynamic bind
    get_pk: function(e){
        return $(e).data("view").model.get("pk") || null;
    }, 
    get_page: function(){
        return get_page();
    }, 
    get_data: function(e){
        return $(e).data("view").model.get("data") || {};
    }, 
    set_data: function(e, data){
        return $(e).data("view").model.set("data", data);
    }, 
    attach_highlight: function(e){
        return LayoutService.attach_highlight(null, $(e));
    }, 
    attach_managed: function(e){
        return $(e).addClass("managed")
    }, 
    get_display_order: function(e){
        return $(e).data("view").model.get_display_order();
    }
});

var LayoutService = (function(){
    var cache = {};
    var is_highlight_enable = true
    return {
        highlight_enable: function(){
            $(".selected").removeClass("selected");
            is_highlight_enable = true;
        }, 
        highlight_disable: function(){
            is_highlight_enable = false;
        }, 
        attach_highlight: function(key, elts){
            if(key == null || !cache[key]){
                cache[key] = true;
                setTimeout(function(){
                    elts.live("mouseover", function(){
                        if(is_highlight_enable){
                            $(this).addClass("selected");
                        }
                    });
                    elts.live("mouseleave", function(){
                        $(this).removeClass("selected");
                    });
                }, 0);
            }
        }
    };
})();

var InfoService = {
    get_name: function(e){
        return $(e).attr("id");
    }, 
    get_uniq_id: function(e){
        return $(e).attr("cid");
    }, 
    is_dropped_widget: function(e){
        return $(e).hasClass("dropped-widget");
    }, 
    is_widget: function(e){
        return $(e).hasClass("widget");
    }
};

var DroppedWidget = Backbone.Model.extend({
    url: function(){
        return ApiUrlMapping.Widget+"/"+this.get("name");
    }, 
    defaults: function(){
        return {
            pk: null, //conflict?
            name: "dummy", 
            page_id: get_page(), 
            data: {}
        }
    }, 
    isNew: function(){
        return !this.get("pk")
    }, 
    get_display_order: function(){
        this.trigger("display_order", this);
        return this.get("display_order");
    }
});

var CloseWidgetView = Backbone.View.extend({
    initialize: function(){
        this.model.bind("destroy", this.remove, this);
    }, 
    on_close_button_clicked: function(){
        if(confirm("このwidgetを消します。このwidgetに登録したデータも消えます。良いですか？")){
            // this.model.isNew = function(){return false;}; //
            this.model.destroy();
        }
    }, 
    remove: function(){
        // delete api?
        $(this.el).remove();
    }
})

var OnCloseHandler = [];

var WidgetDialogView = Backbone.View.extend({
    initialize: function(){
        this.model.bind("update_widget", this.update_widget_layout_edit, this);
        this.edit_button = this.$(".edit");
        this.close_dialog = null;
        var self = this;
        var opts={
            onClose: function(){self.on_close_dialog();}, 
            onLoad: function(){self.on_dialog();}, 
            onBeforeLoad: function(){
			    self.dialog = this.getOverlay().find(".contentWrap");
                self.close_dialog = self.edit_button.data("overlay").close;
                self.on_load_dialog();
            }, 
        };
        this.edit_button.overlay(opts);
    }, 
    prepare_widget_module: function(opt){
        var wname = this.model.get("name");
        var wmodule = widget.get(wname);
        if(!wmodule){ return false}
        var params = {
            dialog: this.dialog, 
            where: $(this.el), 
            widget_name: wname
        }
        if(!!opt){_.extend(params, opt)}
        var we = wmodule.create_context(params);
        return function(method_name){
            var args = Array.prototype.slice.call(arguments);
            args[0] = we;
            return wmodule[method_name].apply(wmodule, args);
        }
    }, 
    on_load_dialog: function(){
        if(this.close_dialog == null){
            throw "overlay close() is not found"
        }
        var wmodule = this.prepare_widget_module();
        if(!!wmodule){
            this.close_dialog_sync();
            OnCloseHandler.push(this.create_on_close_dialog_thunk(wmodule));
            return wmodule("load_page");
        }
    }, 
    on_dialog: function(){
        var self = this;
        var wmodule = this.prepare_widget_module({
            finish_dialog: function(choiced){self.on_widget_selected(choiced);}
        })
        if(!!wmodule){
            return setTimeout(function(){wmodule("on_dialog");}, 0);
        }
    }, 
    create_on_close_dialog_thunk: function(wmodule){
        var self = this;
        return function(){
            if(!!wmodule){
                wmodule("cancel");
                wmodule("on_close");
                _.each(self.dialog.children(), function(e){ $(e).remove();});
            }
        };
    },  
    close_dialog_sync: function(){
        while(OnCloseHandler.length > 0){
            var close_fn = OnCloseHandler.shift()
            if(!!close_fn){close_fn();}
        }
    }, 
    on_close_dialog: function(){
        return setTimeout(this.close_dialog_sync, 0);
    }, 
    on_widget_selected: function(choiced_elt){
        var wmodule = this.prepare_widget_module();
        if(!!wmodule){
            var data = wmodule("collect_data", choiced_elt);
            this.model.set("data", data);
            this.close_dialog();
            var self = this;
            this.model.save().done(function(data){
                self.model.set("pk", data.pk) // pk
                self.model.id = self.model.get("pk");
                self.model.trigger("update_widget", self.model);
            })
        }
    }, 
    update_widget_layout_edit: function(){
        $(this.el).addClass("edited");
        //本当はこの後の処理もmoduleにやらせたい
    }
})

var DroppedWidgetView = (function(){
    is_live_event_bound = false;

    return Backbone.View.extend({
        className: "dropped-widget", 
        initialize: function(){
            this.initialize_once();
            this.model.bind("change", this.render, this);
            $(this.el).data("view", this);
        }, 
        after_render_initialize: function(){
            this.close_view = new CloseWidgetView({el: this.el, model: this.model});
            this.dialog_view = new WidgetDialogView({el: this.el, model: this.model});
        }, 
        initialize_once: function(){
            if(!is_live_event_bound){
                is_live_event_bound = true;
                // element毎のeventは重くなるので
                var self = this;
                setTimeout(function(){
                    LayoutService.attach_highlight("dwidget", $("."+self.className));
                    $("."+self.className+" .close").live("click", function(){
                        var dw = $(this).parent("."+self.className);
                        $(dw).data("view").close_view.on_close_button_clicked();
                    });
                }, 0);
            }
        }, 
        template: _.template([
            '<%= name%>', 
            '<a class="close"></a>', 
            '<a class="edit" rel="#overlay"></a>', 
        ].join("\n")), 
        render: function(){
            var e = $(this.el).html(this.template(this.model.toJSON()));
            e.attr("cid", this.model.cid).draggable({
                revert: true,
                cancel: "a", 
                distance: 5, 
                start: LayoutService.highlight_disable, 
                stop: LayoutService.highlight_enable
            });
            this.after_render_initialize();
            return this;
        }
    })})();

function check(prefix, b){
    console.log(prefix);
    _.each(b.get("widgets"), function(x){!!x && console.log("\t"+x.get("name"))});
}
var Block = Backbone.Model.extend({
    // attribute: //widgets, name
    defaults: function(){
        return {
            name: "dummy", 
            widgets: [], 
        }
        // check("defaults", this);
    }, 
    is_empty: function(){
        var arr = this.get("widgets");
        var n = 0;
        for(var i=0, j=arr.length; i<j; i++){
            if(!!arr[i]){n++;}
        }
        return n <= 0;
    }, 
    pop_by_cid: function(cid){
        // check("pre pop_by_cid", this);
        var arr = this.get("widgets");
        for(var i=0, j=arr.length; i<j; i++){
            if(!!arr[i] && cid == arr[i].cid){
                var r = arr[i];
                arr[i] = null;
                return r;
            }
        }
    }, 
    pop_it: function(dwidget){
        this.pop_by_cid(dwidget.cid);
    }, 
    // update_pk: function(dwidget){
    //     var i = this.get_index(dwidget);
    //     this.get("widgets")[i]
    //     dwidget.get("pk")
    // }, 
    add_widget: function(dwidget){
        // check("pre add_widget", this);
        this.get("widgets").push(dwidget);
        dwidget.bind("display_order", this.get_display_order, this);
        // check("post add_widget", this);
    }, 
    get_display_order: function(dwidget){
        var no = 0;
        for(var i=0, j=arr.length; i<j; i++){
            if(!!arr[i]){
                if(arr[i].cid == dwidget.cid){
                    dwidget.set("display_order", no);
                }
                no++;
            }
        }
        throw "get_display_order: match widget is not found";
    }, 
    get_index: function(dwidget){
        var arr = this.get("widgets");
        for(var i=0, j=arr.length; i<j; i++){
            if(!!arr[i] && arr[i] == dwidget)
                break;
        };
        return i;
    }, 
    move: function(dst, dwidget){
        // check("pre move", this);
        var i = this.get_index(dwidget);
        dst.push(arr.pop(i));
        $(this).trigger("move", src, dst);
        // check("post move", this);
    }
});

var BlockView = Backbone.View.extend({
    initialize: function(){
        this.model.bind("add", this.add_one, this);
    }, 
    change_number_of_item: function(){
        // too cost
        if(this.model.is_empty()){
            $(this.el).addClass("noitem");
        } else {
            $(this.el).removeClass("noitem");
        }
    }, 
    find_by_cid: function(cid){
        return this.$("[cid="+cid+"]");
    }, 
    add_one: function(dwidget){
        var view = new DroppedWidgetView({model: dwidget});
        view.model.bind("destroy", this.change_number_of_item, this);
        $(this.el).append(view.render().el);
        this.change_number_of_item();
    }, 
});

var PaletView = Backbone.View.extend({
    initialize: function(){
        this.$(".widget").draggable({
            revert: true,
            distance: 5, 
            start: LayoutService.highlight_disable, 
            stop: LayoutService.highlight_enable
        });
        LayoutService.attach_highlight("palet", this.$(".widget"));
    }
});

var BlockSheet = Backbone.Model.extend({
    url: ApiUrlMapping.BlockSheet, 
    isNew: function(){return false;}, 
    load_data: function(){
        var self = this;
        this.fetch().done(function(data){
            self.after_load_success(data);
        });
    }, 
    after_load_success: function(data){
        var blocks = data.loaded;
        if(!data.loaded){
            return;
        }
        for(var block_name in blocks){
            if(blocks.hasOwnProperty(block_name)){
                var widgets = blocks[block_name];
                for(var i=0, j=widgets.length; i<j; i++){
                    this.add(block_name, new DroppedWidget(widgets[i]), true)
                }
            }
        }
        // this.trigger("load_success", data);
    }, 
    defaults: function(){
        return {
            blocks: {}, 
            reverse_map: {}
        };
    }, 
    //blocks, reverse_map
    initializeBlock: function(block_name){        
        var block = new Block();
        block.set("name", block_name);
        this.get("blocks")[block_name] = block;
        return block;
    }, 
    toJSON: function(){
        // if block is not saved. ?(now, a default of pk value is 0. so id is 0)
        var r = {}
        var blocks = this.get("blocks")
        for(k in blocks){
            if(blocks.hasOwnProperty(k)){
                r[k] = _.map(_.compact(blocks[k].get("widgets")), 
                             function(e){return {pk: e.get("pk"), name: e.get("name")}});
            }
        }
        return {"structure": r,  "page": get_page()} //get_page is generated by template(edit_page.mak)
    }, 
    after_destroy: function(dw){
        var block_name = this.get("reverse_map")[dw.cid]
        this.get("blocks")[block_name].pop_it(dw);
        this.save();
    }, 
    update_widget_data: function(dw){
        // var block_name = this.get("reverse_map")[dw.cid];
        // this.get("blocks")[block_name].update_data(dw);
        this.save()
    }, 
    add: function(block_name, dwidget, nosave){
        dwidget.bind("destroy", this.after_destroy, this);
        dwidget.bind("update_widget", this.update_widget_data, this)
        this.get("blocks")[block_name].add_widget(dwidget);
        this.get("reverse_map")[dwidget.cid] = block_name;
        if(!nosave){this.save();}
        this.trigger("add", block_name, dwidget);
    }, 
    move: function(block_name, cid){
        var old_block_name = this.get("reverse_map")[cid];
        var blocks = this.get("blocks");
        var dwidget =  blocks[old_block_name].pop_by_cid(cid);
        // check("pre move(src)", blocks[old_block_name]);
        // check("pre move(dst)", blocks[block_name]);
        blocks[block_name].add_widget(dwidget);
        this.get("reverse_map")[dwidget.cid] = block_name;
        this.trigger("move", old_block_name, block_name, dwidget);
        this.save();
        // check("post move(src)", blocks[old_block_name]);
        // check("post move(dst)", blocks[block_name]);
    }, 
});

var BlockSheetView = Backbone.View.extend({
    initialize: function(){
        this.model = new BlockSheet;
        this.model.bind("add", this.add_one, this);
        this.model.bind("move", this.move_one, this);
        // this.model.bind("load_success", this.after_load_success, this);
        // this.model.bind("load_fail", this.after_load_fail, this);
        this.views = {};
        this.initialize_bloks(this.$(".block"));
        this.model.load_data();
    }, 
    add_one: function(block_name, dwidget){
        this.views[block_name].add_one(dwidget);
    }, 
    move_one: function(src, dst, model){
        var e = this.views[src].find_by_cid(model.cid)
        this.views[src].change_number_of_item();
        $(this.views[dst].el).append(e);
        this.views[dst].change_number_of_item();
    }, 
    // after_load_success: function(model){
    // }, 
    // after_load_fail: function(model){
    // }, 
    initialize_bloks: function(block_elts){
        var self = this;
        // LayoutService.attach_highlight("block", block_elts);
        _.each(block_elts, function(e){
            var name = InfoService.get_name(e);
            var block = self.model.initializeBlock(name);
            self.views[name] = new BlockView({el: $(e), model: block});
        });
        block_elts.droppable({
            drop: function(ev, ui){
                if(InfoService.is_dropped_widget(ui.draggable)){
                    self.drop_from_block(ui.draggable, this);
                } else if(InfoService.is_widget(ui.draggable)){
                    self.drop_from_palet(ui.draggable, this);
                }
            }
        });
    }, 
    drop_from_palet: function(draggable, droppable){
        var block_name = InfoService.get_name(droppable);
        var widget_name = InfoService.get_name(draggable)
        var dwmodel = new DroppedWidget({name: widget_name});
        this.model.add(block_name, dwmodel);
    }, 
    drop_from_block: function(draggable, droppable){
        var block_name = InfoService.get_name(droppable);
        // console.log("drop:: "+ $(draggable).html());
        var cid = InfoService.get_uniq_id(draggable);
        this.model.move(block_name, cid);
    }, 
});

var AppView = Backbone.View.extend({
    tagName: "body", 
    initialize: function(){
        this.PaletView = new PaletView({el: $("#widget_palet")});
        this.BlockSheetView = new BlockSheetView({el: $("#wrapped")});
    }
});

function info(){console.log(JSON.stringify(window.AppView.BlockSheetView.model));};

$(function(){
    window.AppView = new AppView()
});