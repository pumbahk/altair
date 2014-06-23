// static/spin.js
// altair/spinner.js

if (!window.component){
    window.component = {};
    window.component.api = {};
}


(function(api){
    api.AjaxComponentView = Backbone.View.extend({
        events: {"click": "onClick"}, 
        /*
        new _({el: <>, model: <>,  modelArea: <>, href: <>, header: <>,  footer: <>,  callback: <>, option: <>})
        */
        initialize: function(opts){
            this.loaded = false;

            this.$componentArea = $(opts.componentArea) || this.$el.attr("data-target");
            if(this.$componentArea.length<=0) throw "componentArea is not found";
            this.href = opts.href || this.$el.attr("href");
            if(!this.href) throw "href is not found";

            this.header = opts.header;
            this.footer = opts.footer;
            this.option = opts.option; // component option

            this.callback = opts.callback;
        }, 
        tmpl_header: '<div class="component-header">',
        tmpl_body: '<div class="component-body">',
        tmpl_footer: '<div class="component-footer">',

        onLoad: function(){ // todo: refactoring;
            var wrap = $('<div class="component">');
            wrap.empty();
            if(this.option.stretch){
                this.stretch(wrap);
            }
            var close_button = $('<button>').attr("type","button").attr("class","close").attr("data-dismiss", "component").attr("aria-hidden", "true").text("×");
            if(!!this.header){
                wrap.append($(this.tmpl_header).append(close_button).append($("<h2>").text(this.header)));
            }else{
                wrap.append($(this.tmpl_header).append(close_button));
            }

            var body = $(this.tmpl_body);
            body.load(this.href, function(){
                this.$el.spin(false);
                if(!!this.callback){this.callback(this);}
            }.bind(this));
            wrap.append(body);
            wrap.append($(this.tmpl_footer).text(this.footer || ""));
            this.$componentArea.append(wrap);            
            this.loaded = true;
        }, 
        onClick: function(){
            if(!this.loaded){
                this.$el.spin("large");
                this.onLoad();
            }
            //this.$componentArea.component(this.option || {});
        }, 
        hide: function(){
            //this.$componentArea.component("hide");
        }, 
        stretch: function($e){
	          // var uniwin = {
		        //     width: window.innerWidth || document.documentElement.clientWidth
			      //         || document.body.offsetWidth,
		        //     height: window.innerHeight || document.documentElement.clientHeight
			      //         || document.body.offsetHeight
	          // };
            // var w = uniwin.width*0.9;
            // var h = uniwin.height*0.9;
            // var $e = $e || this.$componentArea.find(".component");
            // $e.width(w).height(h).css("margin-left",-(w/2));
        }
    });
})(window.component.api);
