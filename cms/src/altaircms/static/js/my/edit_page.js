widget.configure({
    dialog: null, //dynamic bind
    widget_name: null, //dynamic bind
    where: null, //dynamic bind
    get_data: function(e){
        return $(e).data("view").model.get("data") || {};
    }, 
    set_data: function(e, data){
        return $(e).data("view").model.set("data", data);
    }, 
    attach_highlight: function(e){
        return $(e).addClass("selected");
    }, 
    attach_managed: function(e){
        return $(e).addClass("managed")
    }, 
    get_block_name: function(e){
        return $(e).data("view").model.get("block_name");
    }, 
    get_orderno: function(e){
        return $(e).data("view").model.getOrderno();
    }
});

var LayoutService = {
    cache: {}, 
    attachHighlight: function(key, elts){
        if(!this.cache[key]){
            this.cache[key] = true;
            setTimeout(function(){
                elts.live("mouseover", function(){
                    $(this).addClass("selected");
                });
                elts.live("mouseleave", function(){
                    $(this).removeClass("selected");
                });
            }, 0);
        }
    }
};

var InfoService = {
    getName: function(e){
        return $(e).attr("id");
    }, 
    getUniqId: function(e){
        return $(e).attr("cid");
    }, 
    isDroppedWidget: function(e){
        return $(e).hasClass("dropped-widget")
    }
};

var DroppedWidget = Backbone.Model.extend({
    getOrderno: function(){
        this.trigger("orderno", this);
        return this.get("roderno");
    }
});

// var DroppedWidgetCollection = Backbone.Collection.extend({
//     model: DroppedWidget
// });

var CloseWidgetView = Backbone.View.extend({
    initialize: function(){
        this.model.bind("destroy", this.remove, this);
    }, 
    onCloseBottonClicked: function(){
        if(confirm("このwidgetを消します。このwidgetに登録したデータも消えます。良いですか？")){
            this.model.destroy();
        }
    }, 
    remove: function(){
        $(this.el).remove();
    }
})

var WidgetDialogView = Backbone.View.extend({
    initialize: function(){
        this.edit_button = this.$(".edit");
        this.close_dialog = null;
        var self = this;
        var opts={
            onClose: function(){self.onCloseDialog();}, 
            onLoad: function(){self.onDialog();}, 
            onBeforeLoad: function(){
			    self.dialog = this.getOverlay().find(".contentWrap");
                self.close_dialog = self.edit_button.data("overlay").close;
                self.onLoadDialog();
            }, 
        };
        this.edit_button.overlay(opts);
    }, 
    prepareWidgetModule: function(opt){
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
            args.unshift(we);
            return wmodule[method_name].apply(wmodule, args);
        }
    }, 
    onLoadDialog: function(){
        if(this.close_dialog == null){
            throw "overlay close() is not found"
        }
        var wmodule = this.prepareWidgetModule();
        if(!!wmodule){
            return wmodule("load_page");
        }
    }, 
    onDialog: function(){
        var self = this;
        var wmodule = this.prepareWidgetModule({
            finish_dialog: function(choiced){self.onWidgetSelected(choiced);}
        })
        if(!!wmodule){
            return setTimeout(function(){wmodule("on_dialog");}, 0);
        }
    }, 
    onCloseDialog: function(){
        var wmodule = this.prepareWidgetModule();
        if(!!wmodule){
            return setTimeout(function(){wmodule("on_close");}, 0);
        }
    }, 
    onWidgetSelected: function(choiced_elt){
        var wmodule = this.prepareWidgetModule();
        if(!!wmodule){
            var data = wmodule("collect_data", choiced_elt);
        }
        this.close_dialog();
        // eidt model with data
    }
})

var DroppedWidgetView = (function(){
    is_live_event_bound = false;

    return Backbone.View.extend({
        className: "dropped-widget", 
        initialize: function(){
            this.initializeOnce();
            this.model.bind("change", this.render, this);
            $(this.el).data("view", this);
        }, 
        afterRenderInitialize: function(){
            this.close_view = new CloseWidgetView({el: this.el, model: this.model});
            this.dialog_view = new WidgetDialogView({el: this.el, model: this.model});
        }, 
        initializeOnce: function(){
            if(!is_live_event_bound){
                is_live_event_bound = true;
                // element毎のeventは重くなるので
                var self = this;
                setTimeout(function(){
                    LayoutService.attachHighlight("dwidget", $(self.className));
                    $("."+self.className+" .close").live("click", function(){
                        var dw = $(this).parent("."+self.className);
                        $(dw).data("view").close_view.onCloseBottonClicked();
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
            e.attr("cid", this.model.cid).draggable({revert: true});
            this.afterRenderInitialize();
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
    isEmpty: function(){
        var arr = this.get("widgets");
        var n = 0;
        for(var i=0, j=arr.length; i<j; i++){
            if(!!arr[i]){n++;}
        }
        return n <= 0;
    }, 
    popByCid: function(cid){
        // check("pre popByCid", this);
        var arr = this.get("widgets");
        for(var i=0, j=arr.length; i<j; i++){
            if(!!arr[i] && cid == arr[i].cid){
                var r = arr[i];
                arr[i] = null;
                return r;
            }
        }
    }, 
    popIt: function(dwidget){
        this.popByCid(dwidget.cid);
    }, 
    addWidget: function(dwidget){
        // check("pre addWidget", this);
        this.get("widgets").push(dwidget);
        dwidget.bind("destroy", this.popIt, this);
        dwidget.bind("orderno", this.getOrderno, this);
        // check("post addWidget", this);
    }, 
    getOrderno: function(dwidget){
        var no = 0;
        for(var i=0, j=arr.length; i<j; i++){
            if(!!arr[i]){
                if(arr[i].cid == dwidget.cid){
                    dwidget.set("orderno", no);
                }
                no++;
            }
        }
        throw "getOrderno: match widget is not found";
    }, 
    move: function(dst, model){
        // check("pre move", this);
        var arr = this.get("widgets");
        for(var i=0, j=arr.length; i<j; i++){
            if(!!arr[i] && arr[i] == model)
                break;
        };
        dst.push(arr.pop(i));
        $(this).trigger("move", src, dst);
        // check("post move", this);
    }
});

var BlockView = Backbone.View.extend({
    initialize: function(){
        this.model.bind("add", this.addOne, this);
    }, 
    changeNumberOfItem: function(){
        // too cost
        if(this.model.isEmpty()){
            $(this.el).addClass("noitem");
        } else {
            $(this.el).removeClass("noitem");
        }
    }, 
    findByCid: function(cid){
        return this.$("[cid="+cid+"]");
    }, 
    addOne: function(dwidget){
        var view = new DroppedWidgetView({model: dwidget});
        view.model.bind("destroy", this.changeNumberOfItem, this);
        $(this.el).append(view.render().el);
        this.changeNumberOfItem();
    }, 
});

var PaletView = Backbone.View.extend({
    initialize: function(){
        this.$(".widget").draggable({revert: true});
        LayoutService.attachHighlight("palet", this.$(".widget"));
    }
});

var BlockSheet = Backbone.Model.extend({
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
    add: function(block_name, dwidget){
        this.get("blocks")[block_name].addWidget(dwidget);
        this.get("reverse_map")[dwidget.cid] = block_name;
        this.trigger("add", block_name, dwidget);
    }, 
    move: function(block_name, cid){
        var old_block_name = this.get("reverse_map")[cid];
        var blocks = this.get("blocks");
        var dwidget =  blocks[old_block_name].popByCid(cid);
        // check("pre move(src)", blocks[old_block_name]);
        // check("pre move(dst)", blocks[block_name]);
        blocks[block_name].addWidget(dwidget);
        this.get("reverse_map")[dwidget.cid] = block_name;
        this.trigger("move", old_block_name, block_name, dwidget);
        // check("post move(src)", blocks[old_block_name]);
        // check("post move(dst)", blocks[block_name]);
    }, 
});

var BlockSheetView = Backbone.View.extend({
    addOne: function(block_name, dwidget){
        this.views[block_name].addOne(dwidget);
    }, 
    moveOne: function(src, dst, model){
        var e = this.views[src].findByCid(model.cid)
        this.views[src].changeNumberOfItem();
        $(this.views[dst].el).append(e);
        this.views[dst].changeNumberOfItem();
    }, 
    initialize: function(){
        var self = this;
        this.model = new BlockSheet;
        this.model.bind("add", this.addOne, this);
        this.model.bind("move", this.moveOne, this);
        this.views = {};

        var block_elts = this.$(".block")
        LayoutService.attachHighlight("block", block_elts);

        _.each(block_elts, function(e){
            var name = InfoService.getName(e);
            var block = self.model.initializeBlock(name);
            self.views[name] = new BlockView({el: $(e), model: block});
        });
        block_elts.droppable({
            drop: function(ev, ui){
                if(InfoService.isDroppedWidget(ui.draggable)){
                    var block_name = InfoService.getName(this);
                    // console.log("drop:: "+ $(ui.draggable).html());
                    var cid = InfoService.getUniqId(ui.draggable);
                    self.model.move(block_name, cid);
                } else {
                    var block_name = InfoService.getName(this);
                    var widget_name = InfoService.getName(ui.draggable)
                    var dwmodel = new DroppedWidget({block_name: block_name, name: widget_name});
                    self.model.add(block_name, dwmodel);
                }
            }
        });
    }, 
});

var AppView = Backbone.View.extend({
    tagName: "body", 
    initialize: function(){
        this.PaletView = new PaletView({el: $("#widget_palet")});
        this.BlockSheetView = new BlockSheetView({el: $("#wrapped")});
    }
});

$(function(){
    window.AppView = new AppView()
});