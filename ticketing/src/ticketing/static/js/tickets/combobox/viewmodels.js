if (!window.combobox)
    window.combobox = {};

combobox.ComboboxViewModel = core.ViewModel.extend({
    initialize: function(){
        this.$el.delegate("select", "change", this.onSelect.bind(this));
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
        }, 
        onSelect: function(){
            var o = this.$el.find("option:selected");
            this.model.selectValue({"name": o.text(), "pk": o.val()});
        }
});