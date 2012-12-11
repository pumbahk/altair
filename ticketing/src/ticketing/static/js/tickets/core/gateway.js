// backbone
if(!window.core)
    window.core = {};

(function(core){
    var ApiCommunicationGateway = function(opts){
        this.apis = opts.apis;
        if (!this.apis) throw "opts.apis is not found";
        this.models = opts.models;
        if (!this.models) throw "opts.models is not found";
        this.initialize.apply(this, arguments);
    };
    _.extend(ApiCommunicationGateway.prototype, Backbone.Events, {
        initialize: function(){}
    });
    ApiCommunicationGateway.extend = Backbone.Model.extend
    core.ApiCommunicationGateway = ApiCommunicationGateway;
})(window.core);