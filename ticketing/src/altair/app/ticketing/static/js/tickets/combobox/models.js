if (!window.combobox)
    window.combobox = {};

combobox.ComboboxSelection = Backbone.Model.extend({
    defaults: {
        label: "<model名>", 
        targetObject: "", 
        candidates: [], 
        result: null // e.g. {name: "foo", pk: "1"}
    }, 
    refresh: function(){
        this.set("result", null); // warning.
        this.set("candidates", []);
    }, 
    setFirstValue: function(){
        var cands = this.get("candidates");
        if(cands.length > 0){
            this.set("result", cands[0]);
        }
    }, 
    changeCandidates: function(data){
        this.set("candidates", _(data).map(function(o){
            return {"name": o.name, "pk": o.pk};
        }));
        this.setFirstValue();
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
