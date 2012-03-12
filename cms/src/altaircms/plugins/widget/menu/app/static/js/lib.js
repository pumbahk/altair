var lib = (function(){
    var Item = Backbone.Model.extend({
        sync: function(){
            //don't sync this object
            return
        }, 
        defaults: function() {
            return {
                label: "リンク名", 
                link: "URL", 
                order: 0, 
            };
        },
    });

    var ItemList = Backbone.Collection.extend({
        model: Item, 
        nextOrder: function(){
            if (!this.length) return 1;
            return this.last().get("order") + 1;
        }, 
        
        comparator: function(item){
            return item.get("order");
        }
    });

    var ItemView = Backbone.View.extend({
        tagName: "tr", 
        className: "item", 
        template: _.template([
            '<td class="label"></td>', 
            '<td class="link"></td>', 
            '<td class="close"><a href="#" class="close">close</a></td>', 
        ].join("\n")), 

        events: {
            "click a.close": "clearSelf"
        }, 

        initialize: function(){
            this.model.bind("change", this.render, this);
            this.model.bind("destroy", this.remove, this);            
        }, 
        render: function(){
            $(this.el).html(this.template(this.model.toJSON()));
            this.setContent();
            return this;
        }, 
        
        setContent: function(){
            var label = this.model.get("label");
            this.$(".label").text(label);

            var link = this.model.get("link");
            this.$(".link").text(link);
            // this.input.bind('blur', _.bind(this.close, this)).val(text);
            // blue is unfocus. todo sample is then saved object
        }, 
        clearSelf: function(){
            this.model.destroy();
        }, 
        remove: function() {
            $(this.el).remove();
        },
    });

    var AppView = Backbone.View.extend({
        // el: $("#app"), 
        initialize: function(){
            this.label_input = this.$("#label_input");
            this.link_input = this.$("#link_input");
            // model
            this.menulist = new ItemList();
            this.menulist.bind("add", this.addOne, this);
        }, 
        
        events: {
            "keypress #label_input": "createOnEnter", 
            "keypress #link_input": "createOnEnter", 
            "click #submit": "collectData",  // todo fix
        }, 
        
        addOne: function(item){
            var view = new ItemView({model: item});
            $(this.el).find("#menulist").append(view.render().el);
        }, 
        
        loadData: function(params){
            var menulist = this.menulist
            _(params).each(function(param){
                menulist.create(param);
            });
        }, 

        collectData: function(){
            return _($(this.el).find("#menulist tr")).map(function(e){
                var e = $(e);
                return {
                    label: e.find(".label").text(), 
                    link: e.find(".link").text()
                };
            });
        }, 

        createOnEnter: function(e){
            var label = this.label_input.val();
            var link = this.link_input.val();
            if (!label || !link || e.keyCode != 13) return;
            this.menulist.create({label: label, link: link});
            this.label_input.val("");
            this.link_input.val("");
        }, 
    });
    return {
        AppView: AppView
    };
})();