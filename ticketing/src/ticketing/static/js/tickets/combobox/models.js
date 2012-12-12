if (!window.combobox)
    window.combobox = {};

combobox.ComboboxSelection = Backbone.Model.extend({
    defaults: {
        targetObject: "", 
        candidates: [], 
        result: null // e.g. {name: "foo", pk: "1"}
    }, 
    refresh: function(){
        this.set("result", null); // warning.
        this.set("candidates", []);
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
