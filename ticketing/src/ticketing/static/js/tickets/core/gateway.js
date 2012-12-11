// backbone
if(!window.core)
    window.core = {};

(function(core){
    var CommunicationGateway = function(opts){
        this.apis = opts.apis;
        if (!this.apis) throw "opts.apis is not found";
        this.models = opts.models;
        if (!this.models) throw "opts.models is not found";
        this.initialize.apply(this, arguments);
    }
    CommunicationGateway.extend = Backbone.Model.extend
    _.extend(CommunicationGateway.prototype, Backbone.Events, {
        initialize: function(){}
    });

    core.CommunicationGateway = CommunicationGateway;
})(window.core);