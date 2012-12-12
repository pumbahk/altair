if (!window.modal){
    window.modal = {};
    window.modal.api = {};
}


(function(api){
    api.AjaxModalView = Backbone.View.extend({
        events: {"click": "onClick"}, 
        initialize: function(opts){
            this.loaded = false;

            this.$modalArea = $(opts.modalArea) || this.$el.attr("data-target");
            if(this.$modalArea.length<=0) throw "modalArea is not found";
            this.href = opts.href || this.$el.attr("href");
            if(!this.href) throw "href is not found";

            this.header = opts.header;
            this.footer = opts.footer;
            this.option = opts.option; // modal option
        }, 
        tmpl_header: '<div class="modal-header">',
        tmpl_body: '<div class="modal-body">',
        tmpl_footer: '<div class="modal-footer">',
        onLoad: function(){
            var wrap = $('<div class="modal">');
            wrap.empty();
            if (!wrap.hasClass("modal")){
                wrap.addClass("modal");
            }
            var close_button = $('<button type="button" class="close" data-dismiss="modal" aria-hidden="true">').text("×");
            wrap.append($(this.tmpl_header).append(close_button).text(this.header || ""));
            wrap.append($(this.tmpl_body).load(this.href));
            wrap.append($(this.tmpl_footer).text(this.footer || ""));
            this.$modalArea.append(wrap);            
            this.loaded = true;
        }, 
        onClick: function(){
            if(!this.loaded){
                $.Deferred().done(function(){
                    
                    this.onLoad();
                }.bind(this)).resolve();
            }
            this.$modalArea.modal(this.option || {});
        }
    });
})(window.modal.api);
