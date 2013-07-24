// core.ViewModel
// core.CommunicationGateway
if (!window.combobox)
    window.combobox = {}

combobox.ApplicationView = Backbone.View.extend({
    initialize: function(opts){
        this.models = opts.models;
        if(!this.models) throw "models is not found";
        this.apis = opts.apis;
        if(!this.apis) throw "apis is not found";
        this.view_models = opts.view_models;
        if(!this.view_models) throw "view_models is not found";
        this.gateway = opts.gateway;
        if(!this.gateway) throw "gateway is not found";
    }, 
    setFinishBack: function(fn){
        this.gateway.finishCallback = fn;
    }, 
    getFinishBack: function(){
        return this.gateway.productChanged.bind(this.gateway);
    }, 
    start: function(){
        this.gateway.organization.updateCandidates();
        return this;
    }
});

// event receiver and api user.
combobox.ApplicationViewFactory = function(apis, gateway_impl, $organization, $event, $performance, $product, afterAllSelect){
    var models = {
        organization:  new combobox.ComboboxSelection({targetObject: "organization", label: "Organization"}),
        event:  new combobox.ComboboxSelection({targetObject: "event", label: "イベント"}),
        performance:  new combobox.ComboboxSelection({targetObject: "performance", label: "公演"}),
        product:  new combobox.ComboboxSelection({targetObject: "product", label: "商品"})
    };
    var gateway = new combobox.ForTicketPreviewComboboxGateway({models:models, apis:apis, finishCallback:afterAllSelect  });
    var view_models = {
      organization:  new combobox.ComboboxViewModel({model: models.organization, el: $organization}),
      event:  new combobox.ComboboxViewModel({model: models.event, el: $event}),
      performance:  new combobox.ComboboxViewModel({model: models.performance, el: $performance}),
      product:  new combobox.ComboboxViewModel({model: models.product, el: $product})
    };
    var views = {
      organization:  new combobox.ComboboxView({vms: {input: view_models["organization"]}, model: models.organization, el: $organization}),
      event:  new combobox.ComboboxView({vms: {input: view_models["event"]}, model: models.event, el: $event}),
      performance:  new combobox.ComboboxView({vms: {input: view_models["performance"]}, model: models.performance, el: $performance}),
      product:  new combobox.ComboboxView({vms: {input: view_models["product"]}, model: models.product, el: $product})
    };
    return new combobox.ApplicationView({models: models, apis: apis, view_models: view_models, views: views, gateway:gateway});
};