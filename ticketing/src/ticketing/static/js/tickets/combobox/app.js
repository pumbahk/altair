// core.ViewModel
// core.CommunicationGateway

var ComboboxManager = Backbone.Model.extend({
    defaults: {
        selections: {}
    }
})

var ComboboxElement = Backbone.Model.extend({
    defaults: {
        name: "", 
        pk: null
    }
});

var ComboboxElementCollection = Backbone.Collection.extend({
    model: ComboboxElement, 
})

var ComboboxSelection = Backbone.Model.extend({
    defaults: {
        candidates: [], 
        result: null
    }, 
    changeCandidates: function(data){
        this.get("candidates").reset(_(data).map(function(o){
            return {"name": o.name, "pk": o.pk};
        }));
        this.trigger("*combobox.change.candidates");
    }
});

var CandidatesFetcher = function(opts){
    this.api = opts.api;
    if(!api) throw "api is not found";
    this.selection = opts.selection;
    if(!selection) throw "selection is not found";
    initialize.apply(this, arguments);
}
_.extend(CandidatesFetcher.prorotype, {
    getDependsValues: function(){
        return this.selection.get("result").toJSON(); //name, pk
    }, 
    getCandidates: function(params){
        var self = this;
        return $.get(this.api, params)
            .pipe(preview.ApiDeferredService.rejectIfStatusFail(function(data){
                self.collection.changeCandidates(data.data);
            }))
            .fail(function(){
                this.selection.trigger("*fetcher.fail", self.api, arguments);
            });
    }
})
CandidatesFetcher.extend = Backbone.Model.extend;

var ComboxGateway = core.CommunicationGateway.extend({
    initialize: function(){
        // e.g. EventCandidatesFetcher(EventSelection)
        this.organization = this.organization;
        this.event = this.event;
        this.performance = this.performance;
        this.product = this.product;
    }, 
    _apiFail: function(s, err){
        console.warn(s.responseText, arguments);
        this.preview.cancelRendering();
    }, 
    selectOrganization: function(){
        throw "not called";
    }, 
    selectEvent: function(){ //selecting event.
        var self = this;
        return $.get(this.apis.event_list, {"organization": this.organization.get("pk")})
            .pipe(preview.ApiDeferredService.rejectIfStatusFail(function(data){
                self.event.changeCandidates(data.candidates);
            }))
            .fail(this._apiFail.bind(this));
    }, 
    selectPerformance: function(){
    }, 
    selectProduct: function(){
    }
})