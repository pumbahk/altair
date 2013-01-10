// backbone
if(!window)
    window.core = {};

(function(core){
    var ViewModel = function(options){
        this.cid = _.uniqueId("viewmodel");
        this.model = options.model;
        this.el = options.el;
        this.$el = $(this.el);
        this.initialize.apply(this, arguments);
    };

    ViewModel.extend = Backbone.Model.extend
    _.extend(ViewModel.prototype, Backbone.Events, {
        initialize: function(){}
    });
    core.ViewModel = ViewModel;
})(window.core);

