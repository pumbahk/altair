// core.ViewModel
// core.CommunicationGateway

var ComboboxSelection = Backbone.Model.extend({
    defaults: {
        targetObject: "", 
        candidates: [], 
        result: null // e.g. {name: "foo", pk: "1"}
    }, 
    changeCandidates: function(data){
        this.set("candidates", _(data).map(function(o){
            return {"name": o.name, "pk": o.pk};
        }));
        this.trigger("*combobox.change.candidates", this.get("candidates"));
    }, 
    selectValue: function(result){
        this.set("result", result);
        this.trigger("*combobox.select.result");
    }, 
    cascade: function(){
        args = Array.prototype.slice.apply(arguments);
        args.unshift("*combobox.cascade");
        this.trigger.apply(this, args);
    }
});

var CandidatesFetcher = function(opts){
    this.api = opts.api;
    if(!this.api) throw "api is not found";
    this.model = opts.model;
    if(!this.model) throw "model is not found";
    this.initialize.apply(this, arguments);
};
// cascade functions.
_.extend(CandidatesFetcher.prototype, {
    initialize: function(opts){
        this.depends = opts.depends || [];

        if(this.depends.length>0){
            _(this.depends).each(function(dep){
                dep.model.on("*combobox.cascade", this.cascade, this);
            }.bind(this));
            this.depends[0].model.trigger("*combobox.cascade", ":");
        }
    }, 
    cascade: function(){ // cascade event
        // console.log("cascade:"+ this.model.get("targetObject"));
        // console.log(Array.prototype.slice.apply(arguments));
        this.model.trigger.apply(this.model, Array.prototype.slice.apply(arguments));
    }, 
    getDependsValues: function(params){
        var params = params || {};
        _(this.depends).each(function(o){params[o.model.get("targetObject")] = o.model.get("result").pk});
        return params;
    }, 
    getCandidates: function(params){
        var params = this.getDependsValues(params);
        var self = this;
        return $.get(this.api, params)
            .pipe(preview.ApiDeferredService.rejectIfStatusFail(function(data){
                self.model.changeCandidates(data.data);
            }))

            .fail(function(){
                this.model.trigger("*combobox.fetcher.fail", self.api, arguments);
            });
    }, 
    getResult: function(){
        return this.model.get("result");
    }
});
CandidatesFetcher.extend = Backbone.Model.extend;

// event receiver and api user.

var ForTicketPreviewComboxGateway = core.ApiCommunicationGateway.extend({
    initialize: function(opts){
        this.finishCallback = opts.finishCallback;
        if(!this.finishCallback) throw "finishCallback is not found";        

        this.organization = new CandidatesFetcher({api: this.apis.organization_list, depends: [], model: this.models.organization});
        this.event = new CandidatesFetcher({api: this.apis.event_list, depends: [this.organization], model: this.models.event});
        this.performance = new CandidatesFetcher({api: this.apis.performance_list, depends: [this.organization, this.event], model: this.models.performance});
        this.product = new CandidatesFetcher({api: this.apis.product_list, depends: [this.organization, this.event, this.performance], model: this.models.product});
        this.organization.model.on("*combobox.select.result", this.organizationChanged, this);
        this.event.model.on("*combobox.select.result", this.eventChanged, this);
        this.performance.model.on("*combobox.select.result", this.performanceChanged, this);
        this.product.model.on("*combobox.select.result", this.productChanged, this);

        this.organization.model.on("*combobox.fetcher.fail", this.organizationChanged, this);
        this.event.model.on("*combobox.fetcher.fail", this.eventChanged, this);
        this.performance.model.on("*combobox.fetcher.fail", this.performanceChanged, this);
        this.product.model.on("*combobox.fetcher.fail", this.productChanged, this);
    }, 
    _apiFail: function(s, err){
        console.warn(s.responseText, arguments);
        this.preview.cancelRendering();
    }, 
    organizationChanged: function(){
        this.models.event.changeCandidates(this.event.getCandidates());
    }, 
    eventChanged: function(){
        this.models.performance.changeCandidates(this.performance.getCandidates());
    }, 
    performanceChanged: function(){
        this.models.product.changeCandidates(this.product.getCandidates());
    }, 
    productChanged: function(){
        this.finishCallback({
            organization: this.organization.getResult(), 
            event: this.event.getResult(), 
            performance: this.performance.getResult(), 
            product: this.product.getResult()
        });
    }, 
});

var ComboboxViewModel = core.ViewModel.extend({
    initialize: function(){
        this.$el.delegate("select", "change", this.onSelect.bind(this));
        this.model.on("*combobox.change.candidates", this.draw, this);
        this.model.on("*combobox.refresh.candidates", this.refresh, this);
    }, 
    refreshChild: function(){
        this.model.cascade("*combobox.refresh.candidates");
    }, 
    refresh: function(){
        this.$el.empty();
    }, 
    draw: function(candidates){
        this.refresh();
        var root = $("<select>");

        _(candidates).each(function(c){
            root.append($("<option>").text(c.name).attr("value", c.pk));
        });
        this.$el.append(root);
        this.refreshChild();
    }, 
    onSelect: function(){

        var o = this.$el.find("option:selected");
        this.model.selectValue({"name": o.text(), "pk": o.val()});
    }
})
var ComboboxView = Backbone.View.extend({
    initialize: function(opts){
        this.vms = opts.vms;
        this.models = opts.models;
    }
});