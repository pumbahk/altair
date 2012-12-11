if (!window.preview)
    window.preview = {};

(function(preview){
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
            this.set("data", imgdata)
            this.trigger("*preview.update.rendering")
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
        }, 
        updateVars: function(vars){
            this.get("vars").reset(_(vars).map(function(k){
                return {name: k, value: ""};
            }));
            this.trigger("*vars.update.vars");
        }, 
        commitVarsValues: function(){
            if(this.get("vars").length <= 0){
                return this.trigger("*vars.commit.vars", {});
            }
            var var_values = {};
            _(this.get("vars").models).each(function(m){
                var_values[m.get("name")] = m.get("value");
            });
            return this.trigger("*vars.commit.vars",  var_values);
        }
    });
})(window.preview);
