// @require backbone.js
// @require jquery.js
// @require jquery-ui.js (draggble, droppable)
// @require jquery-tools (overlay)
// @require ./backbone_patch.js

/*
TODO:
 get_url function change to implicit fetch method (backbone).
 append design effect.
*/


var InfoService = {
    get_name: function(e){
        return $(e).attr("id");
    }, 
    get_jname: function(name){
        return  NameToJName[name];
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


/*
*** Model ***

model structure is 
{
  Palet: {widgets: [WidgetSource]}, 
  BlockSheet: {
    blocks: {
      widgets: [Widget]
    }
  }
}
*/

LoggedModel = Backbone.Model.extend({
    initialize:function(opts){
        LoggedModel.__super__.initialize.call(this, opts);
        try{
            console.log("initialize model: "+_.keys(opts)+ " -- "+_.values(opts));
        } catch(e){console.error(e)}
    }
});
LoggedView = Backbone.View.extend({
    initialize:function(opts){
        LoggedView.__super__.initialize.call(this, opts);
        if(!!this.$el){this.$el.data("view", this);}
        try{
            console.log("initialize view: "+_.keys(opts)+" -- "+_.values(opts));
        } catch(e){console.error(e)}
    }
});

var MyModel = LoggedModel;
var MyView = LoggedView;

var Palet = MyModel.extend({
    defaults: function(){
        return {
            sources: {}
        };
    }, 
    register: function(source){
        this.get("sources")[source.cid] = source;
        source.parent = this;
        this.trigger("*Palet.sources.register", source);
    }
});

var WidgetSource = MyModel.extend({
    defaults: function(){
        return {
            parent: null, 
            name: "dummy", 
            jname: "ダミー", 
        };
    }, 
    get_url: function(){
        return ApiUrlMapping.Widget+"/"+this.get("name");
    }, 
    describe: function(){
        return this.get("jname");
    }
});

var BlockSheet = MyModel.extend({
    defaults: function(){
        return {
            blocks: {}
        };
    }, 
    get_url: function(){
        return ApiUrlMapping.BlockSheet;
    },
    as_structure: function(){
        alert("heh");
    }, 
    append: function(block){
        this.get("blocks")[block.cid] = block;
    }
});

var Block = MyModel.extend({
    defaults: function(){
        return {
            name: "dummy", 
            parent: null,  // block sheet
            widgets: []
        };
    }, 
    pop: function(w, balancep){
        var widgets = this.get("widgets")
        var i = w.get_index();
        widgets[i] = null;
        // this.set("widgets", _(widgets).compact());
        if(balancep){
            this.balance();
        }
    }, 
    append: function(w){
        this.get("widgets").push(w)
        w.parent = this;
        this.trigger("*block.append.widget", w);
        this.balance();
    }, 
    insert: function(w){
        this.get("widgets").push(w)
        w.parent = this;
        this.balance();
    }, 
    balance: function(){
        this.trigger("*block.balance");
    }, 
    reorder_by_cid: function(order_cid_list){
        console.log("block "+this.get("name")+" -- args: "+ order_cid_list);
        console.log("  order -- before: "+_(this.get("widgets")).map(function(w){return w.cid;}));
        var D = {}
        _(this.get("widgets")).each(function(w){D[w.cid] = w});
        this.set("widgets", _.chain(order_cid_list).compact().map(function(cid){return D[cid];}).value());
        console.log("  order -- after: "+_(this.get("widgets")).map(function(w){return w.cid;}));
    }
});

var Widget = MyModel.extend({
    defaults: function(){
        return {
            parent: null,  // block object
            pk: null, // conflict?
            page_id: get_page(), 
            source: null,  // widget source
            memo: "" // memo text
        }
    }, 
    is_new: function(){
        return !this.get("pk")
    }, 
    get_url: function(){
        return this.source.get_url();
    }, 
    describe: function(){
        var memo = this.get("memo");
        if(!!memo){
            return memo;
        } else {
            return this.get("source").describe()+": "+this.cid;
        }
    }, 
    get_index: function(){
        var cid = this.cid;
        return _(this.widgets).find(function(w){return w.cid == cid});
    }, 
    move: function(dst){
        console.log(this.parent.get("name"), dst.get("name"));
        this.parent.pop(this, this.parent != dst);
        console.log(this.parent.get("name"), dst.get("name"));
        dst.insert(this);
    }
});

var DroppedWidget = MyModel.extend({
    defaults: function(){
        return {
            pk: null, //conflict?
            name: "dummy", 
            jname: "ダミー", 
            page_id: get_page(), 
            data: {}
        }
    }, 
});

/*
** view **
*/

var modelViewBinder = function(model, view){
    return {
        Model: model,
        View: view, 
        create: function(parentView, el){
            var view = new this.View({parent:parentView, el:el});
            if(!view.createModel){
                throw view.toString()+" does not have `createModel()`";
            }
            view.model = view.createModel(this.Model);
            return view;
        }
    }
};


var PaletView = MyView.extend({
    initialize: function(opts){
        PaletView.__super__.initialize.call(this, opts);
        this.appView = opts.appView;
        this.$widgets = opts.$widgets;
        this.sourceCreator = opts.sourceCreator || modelViewBinder(WidgetSource, WidgetSourceView);
        this.registerWidgetSources(this.$widgets);
    }, 
    registerWidgetSources: function($widgets){
        var self = this;
        _($widgets).each(function(el){
            var sourceView = self.sourceCreator.create(self, el);
        });
        $widgets.draggable({
            connectToSortable: ".block", 
            helper: function(el, ev){
                var $el = $(this);
                var helper = $el.clone().removeAttr("id").attr("id", "widgethelper");
                helper.data("view", $el.data("view"));
                return helper;
            }, 
            revert: 'invalid', 
            distance: 5, 
            start: LayoutService.highlight_disable, 
            stop: LayoutService.highlight_enable
        });
        LayoutService.attach_highlight("palet", $widgets);
    }
})

var WidgetSourceView = MyView.extend({
    initialize: function(opts){
        WidgetSourceView.__super__.initialize.call(this, opts);
        this.parent = opts.parent;
    }, 
    onMoved: function(blockView, ui){
        $(ui.item).remove();
        blockView.model.append(new Widget({source: this.model}));
    }, 
    createModel: function(Model){
        var name = InfoService.get_name(this.$el);
        var jname = InfoService.get_jname(name);
        return new Model({name:name, jname:jname, parent:this.parent.model});
    }
});

var BlockSheetView = MyView.extend({
    initialize: function(opts){
        BlockSheetView.__super__.initialize.call(this, opts);
        this.appView = opts.appView;
        this.blockCreator = opts.blockCreator || modelViewBinder(Block, BlockView);
        this.$blocks = opts.$blocks;
        this.registerBlocks(this.$blocks);
    }, 
    registerBlocks: function($blocks){
        var self = this;
        _($blocks).each(function(el){
            var blockView = self.blockCreator.create(self, el);
        });
        $blocks.sortable({
            connectWith: ".block", 
            helper: "original", 
            beforeStop: function(ev, ui){
                var el = $(ui.helper);
                if(!(el || !el.data)){return;}
                var view = el.data("view");
                if(!view || !view.onMoved){return;}
                view.onMoved($(this).data("view"), ui);
            }});
    }
});

var BlockView = MyView.extend({
    initialize: function(opts){
        BlockView.__super__.initialize.call(this, opts);
        this.parent = opts.parent;
        //this.model is lazy initialized.
    }, 
    createModel: function(Model){
        var name = InfoService.get_name(this.$el);
        var model = new Model({name: name, parent:this.parent.model});
        model.bind("*block.append.widget", this.onAppendWidget, this);
        model.bind("*block.balance", this.onBalance, this);
        return model
    }, 
    onAppendWidget: function(widget){
        var view = new DroppedWidgetView({model: widget, parent:this});
        view.model.bind("destroy", this.onBalance, this);
        this.$el.append(view.render().el);
    }, 
    findDropWidgetElements: function(){
        return this.$el.find(".dropped-widget:not(.ui-sortable-placeholder)");
    }, 
    onBalance: function(){
        return this._onBalance(10);
    }, 
    _onBalance: function(n){
        var $widgets = this.findDropWidgetElements();
        var curLen = $widgets.length;
        if ((curLen > 0) && (this.$el.find(".dropped-widget.update-mark").length <= 0)){
            var self = this;
            if(n > 0){
                return setTimeout(function(){return self._onBalance(n-1);}, 100);
            }else{
                alert("fail. rebalance.");
            }
        } else{
            if(curLen <= 0){
                this.$el.addClass("noitem");
            }else{
                this.$el.removeClass("noitem");
            }
            this.model.reorder_by_cid(_($widgets).map(function(e){return $(e).attr("cid");}));
            $widgets.removeClass("update-mark");
        }
    }
});

var DroppedWidgetView = MyView.extend({
    className: "dropped-widget", 
    template: _.template([
        '<%= describe%>', 
        '<a class="close"></a>', 
        '<a class="edit" rel="#overlay"></a>', 
    ].join("\n")), 
    initialize: function(opts){
        DroppedWidgetView.__super__.initialize.call(this, opts);
        this.parent = opts.parent;
        this.$el.data("view", this);
    }, 
    render: function(opts){
        var e = $(this.el).html(this.template({describe: this.model.describe()}));
        e.addClass("update-mark").attr("cid", this.model.cid);
        return this;
    }, 
    _onMoved: function(blockView, n){
        var $dst = this.$el.parents(".block");
        if(!!$dst){
            var dstView = $dst.data("view");
            this.parent = dstView;
            this.model.move(dstView.model);
        }else if(n>0){
            setTimeout(function(){this.onMoved(blockView, n-1)}.bind(this), 100);
        }
    }, 
    onMoved: function(blockView){
        this.parent.findDropWidgetElements().addClass("update-mark");
        this.$el.addClass("update-mark");
        this._onMoved(blockView, 10);
    }
});

var AppView = MyView.extend({
    tagName: "body", 
    initialize: function(opts){
        this.PaletView = new PaletView({model:new Palet(), el: $("#widget_palet"), $widgets: $("#widget_palet").find(".widget")});
        this.BlockSheetView = new BlockSheetView({model:new BlockSheet(), el: $("#wrapped"), $blocks: $("#wrapped").find(".block")});
        AppView.__super__.initialize.call(this, opts);
    }
});

function info(){console.log(JSON.stringify(window.AppView.BlockSheetView.model));};

//
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
