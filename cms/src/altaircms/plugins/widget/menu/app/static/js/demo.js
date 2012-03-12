$(function(){
    window.Menu = Backbone.Model.extend({
        defaults: function() {
            return {
                label: "リンク名", 
                url: "URL", 
                order: Menus.nextOrder()
            };
        },
        // toggle: function() {
        //     this.save({done: !this.get("done")});
        // }

    });
    window.MenuList = Backbone.Collection.extend({
        model: Menu,
        localStorage: new Store("menus"),
        done: function() {
            return this.filter(function(menu){ return menu.get('done'); });
        },

        remaining: function() {
            return this.without.apply(this, this.done());
        },
        nextOrder: function() {
            if (!this.length) return 1;
            return this.last().get('order') + 1;
        },

        comparator: function(menu) {
            return menu.get('order');
        }

    });
    window.Menus = new MenuList;
    window.MenuView = Backbone.View.extend({
        tagName:  "li",
        template: _.template($('#item-template').html()),

        events: {
            // "click .check"              : "toggleDone",
            "dblclick div.menu-text"    : "edit",
            "click span.menu-destroy"   : "clear",
            "keypress .menu-input"      : "updateOnEnter"
        },
        initialize: function() {
            this.model.bind('change', this.render, this);
            this.model.bind('destroy', this.remove, this);
        },
        render: function() {
            $(this.el).html(this.template(this.model.toJSON()));
            this.setText();
            return this;
        },
        // To avoid XSS (not that it would be harmful in this particular app),
        // we use `jQuery.text` to set the contents of the menu item.
        setText: function() {
            var text = this.model.get('text');
            this.$('.menu-text').text(text);
            this.input = this.$('.menu-input');
            this.input.bind('blur', _.bind(this.close, this)).val(text);
        },

        // toggleDone: function() {
        //     this.model.toggle();
        // },

        edit: function() {
            $(this.el).addClass("editing");
            this.input.focus();
        },

        close: function() {
            this.model.save({text: this.input.val()});
            $(this.el).removeClass("editing");
        },

        updateOnEnter: function(e) {
            if (e.keyCode == 13) this.close();
        },

        remove: function() {
            $(this.el).remove();
        },

        clear: function() {
            this.model.destroy();
        }
    });

    window.AppView = Backbone.View.extend({
        el: $("#menuapp"),
        statsTemplate: _.template($('#stats-template').html()),
        events: {
            "keypress #new-menu":  "createOnEnter",
            "keyup #new-menu":     "showTooltip",
            "click .menu-clear a": "clearCompleted"
        },
        initialize: function() {
            this.input    = this.$("#new-menu");

            Menus.bind('add',   this.addOne, this);
            Menus.bind('reset', this.addAll, this);
            Menus.bind('all',   this.render, this);

            Menus.fetch();
        },

        render: function() {
            this.$('#menu-stats').html(this.statsTemplate({
                total:      Menus.length,
                done:       Menus.done().length,
                remaining:  Menus.remaining().length
            }));
        },

        addOne: function(menu) {
            var view = new MenuView({model: menu});
            $("#menu-list").append(view.render().el);
        },

        addAll: function() {
            Menus.each(this.addOne);
        },

        createOnEnter: function(e) {
            var text = this.input.val();
            if (!text || e.keyCode != 13) return;
            Menus.create({text: text});
            this.input.val('');
        },

        clearCompleted: function() {
            _.each(Menus.done(), function(menu){ menu.destroy(); });
            return false;
        },

        showTooltip: function(e) {
            var tooltip = this.$(".ui-tooltip-top");
            var val = this.input.val();
            tooltip.fadeOut();
            if (this.tooltipTimeout) clearTimeout(this.tooltipTimeout);
            if (val == '' || val == this.input.attr('placeholder')) return;
            var show = function(){ tooltip.show().fadeIn(); };
            this.tooltipTimeout = _.delay(show, 1000);
        }
    });
    window.App = new AppView;
});
