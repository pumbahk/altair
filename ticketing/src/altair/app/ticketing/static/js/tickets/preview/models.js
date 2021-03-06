if (!window.preview)
    window.preview = {};

(function(preview){
    preview.Resource = Backbone.Model.extend({
        defaults: {
           pk: null,
           label: "<default>",
           format_id: null,
           ticket_formats: [],
        },
        hasTicketFormats: function(){
          return this.get("ticket_formats").length > 0 || !!this.get("format_id");
        }
    });

    preview.TicketFormatManager = Backbone.Model.extend({
      defaults: {
        visibles: [],
        all: {}
      },
      refresh: function(ticket_formats){
        // ticket_formats is [{pk: 1, name: "foo", type: "sej"},....]
        var all = {};
        var visibles = [];
        this.set("all", all);
        this.set("visibles", visibles);
        _.each(ticket_formats, function(d){
          all[d.pk] = d;
          visibles.push(d);
        });
      },
      updateVisibles: function(ticket_formats){
        // xs is [{pk: 1, name: "foo", type: "sej"},...]
        var visibles = [];
        this.set("visibles", visibles);
        alls = this.get("all");
        _.each(ticket_formats, function(d){
          var k = d.pk;
          if(!(alls.hasOwnProperty(k))){
            alls[k] = d;
          }
          visibles.push(d);
        });
        return visibles;
      }
    })

    var NONE_CHANGED = 0;
    var REDRAW_IMAGE = 1;
    var RELOAD_SVG = 2;
    preview.ParameterStore = Backbone.Model.extend({
        defaults:{
            sx: 1.0, 
            sy: 1.0, 
            default_sx: 2.0,  //fetch default
            default_sy: 2.0, 
            ticket_format: null, 
            preview_type: "default", // or "sej"
            holder: null,  //holder is svg data source{name: "", pk: ""}
            changed: NONE_CHANGED
        }, 
        changePreviewType: function(v){
            this.set("preview_type", v)
        },
        changeSx: function(v){ //todo: use this;
            this.set("sx", v);
            if(this.get("default_sx") < v){
                this.set("changed", REDRAW_IMAGE);
            }
        }, 
        changeSy: function(v){
            this.set("sy", v);
            if(this.get("default_sy") < v){
                this.set("changed", REDRAW_IMAGE);
            }
        }, 
        changeTicketFormat: function(v){
            this.set("ticket_format", v);
            this.set("changed", RELOAD_SVG);
            this.trigger("*params.ticket_format.update");
        }, 
        changeHolder: function(h, silent){
            this.set("holder", h);
            this.set("changed", RELOAD_SVG);
            if(!silent){
                this.reDraw();
            }
        }, 
        refreshDefault: function(){
            this.set("default_sx", 2.0);
            this.set("default_sy", 2.0);
            this.set("sx", 1.0);
            this.set("sy", 1.0);
        }, 
        reDraw: function(){
            switch (this.get("changed")) {
            case REDRAW_IMAGE:
                this.trigger("*params.preview.redraw");
                break;
            case RELOAD_SVG:
                if(!this.get("holder")){
                    this.trigger("*params.preview.redraw");
                }else {
                    this.trigger("*params.change.holder");
                }
                break;
            }
        }
    });

    var SVGStage = {"empty":0, "raw":1, "normalize":2, "filled":3};
    var PreviewStage = {"empty": 0, "before":1, "rendering":2, "after": 3};
    preview.SVGStore = Backbone.Model.extend({
        defaults:{
            data: null, 
            normalize: null, 
            stage: SVGStage.empty
        }, 
        _updateValue: function(stage, svg){
            this.set("stage", stage);
            this.set("data", svg);
        }, 
        updateToRaw: function(svg){
            this._updateValue(SVGStage.raw, svg);
            this.set("normalize", null);
            this.trigger("*svg.update.raw");
        }, 
        updateToNormalize: function(svg){
            this._updateValue(SVGStage.normalize, svg);
            this.set("normalize", svg);
            this.trigger("*svg.update.normalize");
        }, 
        updateToFilled: function(svg){
            this._updateValue(SVGStage.filled, svg);
            this.trigger("*svg.update.filled");
        }, 
    });

    preview.PreviewImageStore = Backbone.Model.extend({
        defaults: {
            data: null, //base64
            width: 0,  // this is base_width (sx = 1.0 ). so, real image width is default_sx * width
            height: 0, 
            rendering_width: 0, 
            rendering_height: 0, 
            canceled: false,
            stage: PreviewStage.empty
        }, 
        beforeRendering: function(){
            this.set("stage", PreviewStage.before);
            this.trigger("*preview.update.loading");
        }, 
        cancelRendering: function(){
            this.set("stage", PreviewStage.after);
            this.trigger("*preview.update.cancel");
        }, 
        startRendering: function(imgdata){
            this.set("stage", PreviewStage.rendering);
            this.set("data", imgdata);
            this.trigger("*preview.update.rendering")
        }, 
        isNotShown: function(){
            return String(this.get("width")) == "0" || String(this.get("height")) == "0";
        }, 
        initialImage: function(width, height, rendering_width, rendering_height){
            this.set("width", width);
            this.set("height", height);
            this.set("rendering_width", rendering_width);
            this.set("rendering_height", rendering_height);
        }, 
        resizeImage: function(width, height){
            this.set("rendering_width", width);
            this.set("rendering_height", height);
            this.trigger("*preview.resize");
        }, 
        afterRendering: function(){
            this.set("stage", PreviewStage.after);
            this.trigger("*preview.update.rendered");
        }, 
        reDraw: function(){
            this.trigger("*preview.redraw");
        }
    })

    preview.TemplateVar = Backbone.Model.extend({
        defaults: {
            name: null, 
            value: null
        }
    });
    preview.TemplateVarCollection = Backbone.Collection.extend({
        model: preview.TemplateVar
    });
    preview.TemplateVarStore = Backbone.Model.extend({
        defaults: {
            vars: new preview.TemplateVarCollection(),  //collection
            changed: false 
        }, 
        varsChanged: function(){
            this.set("changed", true);
        }, 
        updateVars: function(vars){
            this.get("vars").reset(_(vars).map(function(k){
                return {name: k, value: ""};
            }));
            this.get("vars").on("change", this.varsChanged, this); // todo: avoid leak
            this.trigger("*vars.update.vars");
        }, 
        commitVarsValues: function(){
            if(this.get("vars").length <= 0){
                return this.trigger("*vars.commit.vars", {});
            }
            var vars_values = this.collectVarsValues();
            return this.trigger("*vars.commit.vars",  vars_values);
        },
        collectVarsValues: function(){
            var var_values = {};
            _(this.get("vars").models).each(function(m){
                var_values[m.get("name")] = m.get("value");
            });
          return var_values;
        }
    });
})(window.preview);
