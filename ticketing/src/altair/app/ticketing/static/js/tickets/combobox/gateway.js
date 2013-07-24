if (!window.combobox)
    window.combobox = {};

(function(combobox){
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
            _(this.depends).each(function(o){
                if(!!o.model.get("result")){
                    params[o.model.get("targetObject")] = o.model.get("result").pk;
                }
            });
            return params;
        }, 
        updateCandidates: function(params){
            var params = this.getDependsValues(params);
            var self = this;
            return this.api(params)
                .pipe(core.ApiService.rejectIfStatusFail(function(data){
                    self.model.changeCandidates(data.data);
                }))
                .fail(function(){
                    self.model.trigger("*combobox.fetcher.fail", self.api, {responseText: self.ap+":"+arguments[0]["responseText"]});
                });
        }, 
        getResult: function(){
            return this.model.get("result");
        }
    });
    CandidatesFetcher.extend = Backbone.Model.extend;

    combobox.ForTicketPreviewComboboxGateway = core.ApiCommunicationGateway.extend({
        initialize: function(opts){
            this.finishCallback = opts.finishCallback;
            if(!this.finishCallback) throw "finishCallback is not found";        

            this.organization = new CandidatesFetcher({api: core.ApiService.asGetFunction(this.apis.organization_list),
                                                       depends: [],
                                                       model: this.models.organization});
            this.event = new CandidatesFetcher({api: core.ApiService.asGetFunction(this.apis.event_list), 
                                                depends: [this.organization], 
                                                model: this.models.event});
            this.performance = new CandidatesFetcher({api: core.ApiService.asGetFunction(this.apis.performance_list),
                                                      depends: [this.organization, this.event],
                                                      model: this.models.performance});
            this.product = new CandidatesFetcher({api: core.ApiService.asGetFunction(this.apis.product_list),
                                                  depends: [this.organization, this.event, this.performance],
                                                  model: this.models.product});

            this.organization.model.on("*combobox.select.result", this.organizationChanged, this);
            this.event.model.on("*combobox.select.result", this.eventChanged, this);
            this.performance.model.on("*combobox.select.result", this.performanceChanged, this);
            this.product.model.on("*combobox.select.result", this.productChanged, this);

            this.organization.model.on("*combobox.fetcher.fail", this._apiFail, this);
            this.event.model.on("*combobox.fetcher.fail", this.apiFail, this);
            this.performance.model.on("*combobox.fetcher.fail", this._apiFail,  this);
            this.product.model.on("*combobox.fetcher.fail", this._apiFail, this);
        }, 
        _apiFail: function(s, err){
            console.warn(s.responseText, arguments);
        }, 
        organizationChanged: function(){
            this.event.updateCandidates();
        }, 
        eventChanged: function(){
            this.performance.updateCandidates();
        }, 
        performanceChanged: function(){
            this.product.updateCandidates();
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
})(window.combobox);