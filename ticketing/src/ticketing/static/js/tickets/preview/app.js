// require backbone.js
// require altair/deferredqueue.js

/// services
var ApiDeferredService = {
    rejectIfStatusFail: function(fn){
        return function(data){
            if (data && data.status){
                return fn? fn(data) : data;
            }else {
                return $.Deferred().rejectWith(this, [{responseText: "status: false, "+data.message}]);
            }
        };
    }, 
};

var DragAndDropSupportService = {
    compose: function(){
        var fns = arguments;
        return function(){
            var r;
            for (var i=0, j=fns.length; i<j; i++){
                r = fns[i].apply(this, arguments);
            }
            return r;
        }
  　},
    cancel: function(e){
        e.stopPropagation();
        e.preventDefault();
    },
    onDrop: function(file_use_fn){
      return function(e){
        var files = e.dataTransfer.files;
        for (var i=0, file; file=files[i]; i++){
          var reader = new FileReader();

          reader.onerror = function(e){ 
           alert('Error code: ' + e.target.error.code);
          }

          reader.onload = (function(aFile){
            return function(e){ //?
              file_use_fn(e);
            }
          })(file);
          reader.readAsText(file, "UTF-8");
        }
        return false;
      }
    },
}

var ConsoleMessage = { //use info, log, warn, error, dir
    success: console.debug, 
    error: console.debug, 
    info: console.debug, 
    warn: console.debug
}

/// models
var SVGStage = {"empty":0, "raw":1, "normalize":2, "filled":3};
var PreviewStage = {"empty": 0, "before":1, "rendering":2, "after": 3};
var SVGStore = Backbone.Model.extend({
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

var PreviewImageStore = Backbone.Model.extend({
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
    }
})

var TemplateVar = Backbone.Model.extend({
    defaults: {
        name: null, 
        value: null
    }
});
var TemplateVarCollection = Backbone.Collection.extend({
    model: TemplateVar
});
var TemplateVarStore = Backbone.Model.extend({
    defaults: {
        vars: new TemplateVarCollection(),  //collection
    }, 
    updateVars: function(vars){
        this.get("vars").reset(_(vars).map(function(k){
            return {name: k, value: ""};
        }));
        this.trigger("*vars.update.vars");
    }
});

var ApiCommunicationGateWay = function(opts){
    this.apis = opts.apis;
    if (!this.apis) throw "opts.apis is not found";
    this.models = opts.models;
    if (!this.models) throw "opts.models is not found";
    this.initialize();
};

_.extend(ApiCommunicationGateWay.prototype, { // view?
    initialize: function(){
        this.preview = this.models.preview;
        this.svg = this.models.svg;
        this.vars = this.models.vars;

        this.svg.on("*svg.update.raw", this.svgRawToX, this);
        this.svg.on("*svg.update.normalize", this.svgNormalizeToX, this);
        this.svg.on("*svg.update.normalize", this.collectTemplateVars, this);
        this.svg.on("*svg.update.filled", this.svgFilledToX, this);
    }, 
    _apiFail: function(s, err){
        alert(s.responseText);
        this.preview.cancelRendering();
    }, 
    svgRawToX: function(){
        this.preview.beforeRendering();
        var self = this;
        return $.get(this.apis.normalize, {"svg": this.models.svg.get("data")})
            .pipe(ApiDeferredService.rejectIfStatusFail(function(data){
                self.svg.updateToNormalize(data.data);
            }))
            .fail(this._apiFail);
    }, 
    svgNormalizeToX: function(){
        this.preview.beforeRendering();
        var self = this;
        return $.get(this.apis.previewbase64, {"svg": this.models.svg.get("data")})
            .pipe(ApiDeferredService.rejectIfStatusFail(function(data){
                self.preview.startRendering("data:image/png;base64,"+data.data); //add-hoc
            }))
            .fail(this._apiFail);
    }, 
    collectTemplateVars: function(){ // todo:move it?
        var self = this;
        $.get(this.apis.collectvars, {"svg": this.models.svg.get("normalize")})
            .pipe(ApiDeferredService.rejectIfStatusFail(function(data){
                self.vars.updateVars(data.data);
            }))
            .fail(this._apiFail);
    }
})

/// viewmodels
var PreviewImageViewModel = Backbone.View.extend({
    draw: function(imgdata){
        this.$el.empty();
        this.$el.append($("<img title='preview' alt='preview todo upload file'>").attr("src", imgdata));
    }
});

var DropAreaViewModel = Backbone.View.extend({ //View?
    touched: function(){
        this.$el.addClass("touched");
    }, 
    untouched: function(){
        this.$el.removeClass("touched")
    }, 
});

var LoadingSpinnerViewModel = Backbone.View.extend({
    loading: function(){
        this.$el.spinner("start");
    }, 
    noloading: function(){
        this.$el.spinner("stop");
    }
});

var TemplateVarRowViewModel = Backbone.View.extend({
    tagName: "tr", 
    className: "vars-row", 
    template: _.template('<td><%- name %></td><td><input name="<%- name %>" value="<%- value %>"></input></td>'), 
    render: function(){
        this.$el.html(this.template(this.model.toJSON())); //redraw is inefficient. todo: fix
        return this;
    }
});

var TemplateVarsTableViewModel = Backbone.View.extend({
    initialize: function(){
        this.$tbody = this.$el.find("tbody");
        this.inputs = [];
    }, 
    redraw: function(vars){
        this.inputs = [];
        this.$tbody.empty();
        _(vars).each(this.addOne.bind(this));
    }, 
    addOne: function(v){
        var row = new TemplateVarRowViewModel({model: v});
        this.inputs.push(row);
        this.$tbody.append(row.render().el);
    }
});

/// views
var DragAndDropSVGSupportView = Backbone.View.extend({
  events: {
  }, 
  initialize: function(opts){
      this.vms = opts.vms || {}
      var compose = DragAndDropSupportService.compose;
      var default_action_cancel = DragAndDropSupportService.cancel;
      
      this.el.addEventListener("dragenter", default_action_cancel, false);
      this.el.addEventListener('dragover',  compose(default_action_cancel, this.vms.droparea.touched.bind(this.vms.droparea)), false);
      this.el.addEventListener('dragleave', compose(default_action_cancel, this.vms.droparea.untouched.bind(this.vms.droparea)), false);
      this.el.addEventListener('drop',
                               compose(default_action_cancel,
                                       this.vms.droparea.untouched.bind(this.vms.droparea), 
                                       DragAndDropSupportService.onDrop(this.onLoadSVG.bind(this))),
                               false);
  }, 
  _onLoadSVGPassed: function(svg){
      this.vms.spinner.loading();
      return this.model.updateToRaw(svg);
  }, 
  onLoadSVG: function(e){
      return this._onLoadSVGPassed(e.target.result)
  }
});

var PreviewImageView = Backbone.View.extend({
    initialize: function(opts){
        this.model.on("*preview.update.loading", this.onLoading, this);
        this.model.on("*preview.update.loading", this.onCancel, this);
        this.model.on("*preview.update.rendering", this.onRendering, this);
        this.vms = opts.vms;
    }, 
    onLoading: function(){
        this.vms.spinner.loading();
    }, 
    onCancel: function(){
        this.vms.spinner.noloading();
    }, 
    onRendering: function(){
        this.vms.spinner.noloading();
        this.vms.preview.draw(this.model.get("data"));
    }
});

var TemplateFillValuesView = Backbone.View.extend({
    initialize: function(opts){
        this.model.on("*vars.update.vars", this.onUpdateTemplateVars, this);
        this.vms = opts.vms;
    }, 
    onUpdateTemplateVars: function(){
        this.vms.vars_input.redraw(this.model.get("vars").models);
    }
});

var ManagementTemplateValuesView = Backbone.View.extend({
});
