if (!window.combobox)
    window.combobox = {};

combobox.ComboboxView = Backbone.View.extend({
    initialize: function(opts){
        this.vms = opts.vms;
        this.model.on("*combobox.change.candidates", this.draw, this);
        this.model.on("*combobox.refresh.candidates", this.refresh, this);
    }, 
    draw: function(candidates){
        this.vms.input.draw(candidates);
        this.refreshChild();
        if (candidates.length <= 1)
            this.vms.input.onSelect();
    }, 
    refresh: function(){
        this.model.refresh();
        this.vms.input.refresh();
    }, 
    refreshChild: function(){
        this.model.cascade("*combobox.refresh.candidates");
    }
});