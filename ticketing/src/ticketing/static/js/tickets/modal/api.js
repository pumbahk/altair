// static/spin.js
// altair/spinner.js

if (!window.modal){
    window.modal = {};
    window.modal.api = {};
}


(function(api){
    api.AjaxModalView = Backbone.View.extend({
        events: {"click": "onClick"}, 
        /*
        new _({el: <>, model: <>,  modelArea: <>, href: <>, header: <>,  footer: <>,  callback: <>, option: <>})
        */
        initialize: function(opts){
            this.loaded = false;

            this.$modalArea = $(opts.modalArea) || this.$el.attr("data-target");
            if(this.$modalArea.length<=0) throw "modalArea is not found";
            this.href = opts.href || this.$el.attr("href");
            if(!this.href) throw "href is not found";

            this.header = opts.header;
            this.footer = opts.footer;
            this.option = opts.option; // modal option

            this.callback = opts.callback;
        }, 
        tmpl_header: '<div class="modal-header">',
        tmpl_body: '<div class="modal-body">',
        tmpl_footer: '<div class="modal-footer">',

        onLoad: function(){ // todo: refactoring;
            var wrap = $('<div class="modal">');
            wrap.empty();
            if (!wrap.hasClass("modal")){
                wrap.addClass("modal");
            }

            var close_button = $('<button>').attr("type","button").attr("class","close").attr("data-dismiss", "modal").attr("aria-hidden", "true").text("×");
            if(!!this.header){
                wrap.append($(this.tmpl_header).append(close_button).append($("<h2>").text(this.header)));
            }else{
                wrap.append($(this.tmpl_header).append(close_button));
            }

            var body = $(this.tmpl_body);
            body.load(this.href, function(){
                this.$el.spin(false);
                if(!!this.callback){this.callback(this.$modalArea);}
            }.bind(this));
            wrap.append(body);
            wrap.append($(this.tmpl_footer).text(this.footer || ""));
            this.$modalArea.append(wrap);            
            this.loaded = true;
        }, 
        onClick: function(){
            if(!this.loaded){
                this.$el.spin("large");
                this.onLoad();
            }
            this.$modalArea.modal(this.option || {});
        }
    });
})(window.modal.api);
