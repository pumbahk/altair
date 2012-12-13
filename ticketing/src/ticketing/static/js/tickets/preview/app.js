// require backbone.js
// require altair/deferredqueue.js
// require core/viewmodel.js
// require core/gateway.js

// require ./models.js
// require ./gateway.js
// require ./preview_api.js
// require ./services.js
// require ./viewmodels.js
// require ./views.js

// todo: auto redraw?
// todo: 見た目綺麗に
// todo: buttonをまともに機能させる
// todo: download
// todo: errorをページ上に表示
// todo: 拡大/縮小

/// services
// give me. module!
if (!window.preview)
    window.preview = {};

preview.ApplicationView = Backbone.View.extend({
    initialize: function(opts){
        this.models = opts.models;
        if(!this.models) throw "models is not found";
        this.apis = opts.apis;
        if(!this.apis) throw "apis is not found";
        this.view_models = opts.view_models;
        if(!this.view_models) throw "view_models is not found";
        this.views = opts.views;
        if(!this.views) throw "views is not found";
        this.gateway = opts.gateway;
        if(!this.gateway) throw "gateway is not found";
    }, 
    reDrawImage: function(){
        this.models.vars.commitVarsValues();
    }, 
    fillsVarsWithParams: function(params){
        this.views.template_fillvalues_view.fillsVarsWithParams(params);
    }
});

preview.ApplicationViewFactory = function(apis,  gateway_impl,  $preview_block,  $preview_area,  $svg_droparea, $template_vars_table, $paramater_settings_area){
       var models = {
           svg: new preview.SVGStore(),
           preview: new preview.PreviewImageStore(),
           vars: new preview.TemplateVarStore(), 
           params: new preview.ParamaterStore()
       };

      var view_models = {
          preview: new preview.PreviewImageViewModel({el: $preview_area}),
          droparea: new preview.DropAreaViewModel({el: $svg_droparea}),
          spinner: new preview.LoadingSpinnerViewModel({el: $preview_area}),
          vars_input: new preview.TemplateVarsTableViewModel({el: $template_vars_table}), 
      };

      var views = {
          dad_view:  new preview.DragAndDropSVGSupportView({el: $svg_droparea, vms: view_models, model: models.svg}), 
          preview_image_view:  new preview.PreviewImageView({el: $preview_block, vms: view_models, model: models.preview}), 
          template_fillvalues_view:  new preview.TemplateFillValuesView({el: $preview_block, vms: view_models, model: models.vars}), 
          params_view: new preview.ParamaterManageView({el: $paramater_settings_area, vms: view_models, model: models.params})
      };

    var gateway = new gateway_impl({models: models, apis: apis});
    return new preview.ApplicationView({models: models, apis: apis, view_models: view_models, views: views, gateway:gateway});
};
