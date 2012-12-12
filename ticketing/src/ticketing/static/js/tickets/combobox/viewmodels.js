if (!window.combobox)
    window.combobox = {};

combobox.ComboboxViewModel = core.ViewModel.extend({
    initialize: function(){
        this.$el.delegate("select", "click", this.onSelect.bind(this)); // click ? change?
        }, 
        refresh: function(){
            this.$el.empty();
        }, 
        draw: function(candidates){
            this.refresh();
            var select = $("<select>");
            _(candidates).each(function(c){
                select.append($("<option>").text(c.name).attr("value", c.pk));
            });
            
            this.$el.append($("<p>").text(this.model.get("label")));
            this.$el.append(select);
        }, 
        onSelect: function(){
            var o = this.$el.find("option:selected");
            this.model.selectValue({"name": o.text(), "pk": o.val()});
        }
});