// model

$(function(){


    var Widget = Backbone.Model.extend({
        defaults: function(){
            return {
                name: "dummy"
            };
        }
    });

    var WidgetCollection = Backbone.Collection.extend({
        model: Widget
    });

    var DroppedWidget = Backbone.Model.extend({
    });

    var DroppedWidgetCollection = Backbone.Collection.extend({
        model: DroppedWidget, 
    });

    var Block = Backbone.Model.extend({
    });

    var BlockCollection = Backbone.Collection.extend({
        model: Block
    });

    var Selectable = Backbone.View.extend({
        events: {
            "mouseenter": "highlight", 
            "mouseleave": "unhighlight", 
        }, 
        unhighlight: function(){
            $(this.el).removeClass("selected")
        }, 
        highlight: function(){
            $(this.el).addClass("selected");
        }
    });

    // view
    var WidgetView = Selectable.extend({
        className: "widget", 
        initialize: function(){
            $(this.el).draggable({revert: true});
        }
    });

    var DroppedWidgetView = Selectable.extend({
        className: ".dropped-widget", 
        render: function(){
            console.log("hoge");
        }, 
    });

    var BlockView = Selectable.extend({
        className: "widget", 
        add_one: function(dw){
            var view = new DroppedWidgetView({model: dw});
            $(this.el).append(view.render().el);
        }, 
        item_template: function(item){
            // itemはdropped`widgetのmodel
            return $("<div class='dropped-widget'>").text(item.get("name"));
        }, 
        initialize: function(){
            this.collection = new DroppedWidgetCollection();
            this.collection.bind("add", this.add_one, this);

            var self = this;
            $(this.el).droppable({
                drop: function(ev, ui){
                    var name = $(ui.draggable).text();
                    self.collection.create({name: name});
                    //$(self.el).removeClass("noitem");
                }
            });
        }
    });

    var AppView = Backbone.View.extend({
        el: $("#wrapped"), 
        initialize: function(){
            _.each($(".widget"), function(e){
                new WidgetView({el: e});
            });
            _.each($(".block"), function(e){
                new BlockView({el: e});
            });
        }, 
        foo: function(){
            console.log("hoo");
        }
    });

    window.App = new AppView;
});


