if (!window.preview)
    window.preview = {}

preview.PreviewImageViewModel = core.ViewModel.extend({
    draw: function(imgdata){
        this.$el.empty();
        var preview_img = $('<img id="preview_img" title="clickして再描画" alt="clickして再描画">').attr('src', imgdata);
        this.$el.append(preview_img);
        this.$el.parents(".empty").removeClass("empty");
    }
});

preview.DropAreaViewModel = core.ViewModel.extend({ //View?
    touched: function(){
        this.$el.addClass("touched");
    }, 
    untouched: function(){
        this.$el.removeClass("touched");
    }, 
});

preview.LoadingSpinnerViewModel = core.ViewModel.extend({
    loading: function(){
        this.$el.spin();
    }, 
    noloading: function(){
        this.$el.spin(false);
    }
});

preview.TemplateVarsTableViewModel = core.ViewModel.extend({
    initialize: function(){
        this.$tbody = this.$el.find("tbody");
        this.inputs = [];
    }, 
    emptyInfoTemplate: _.template('<td><div class="alert alert-info"><%= message %></div></td>'), 
    each_input: function(fn){
        _(this.inputs).each(function(row){
            !!row.left && fn(row.$left, row.left);
            !!row.right && fn(row.$right, row.right);
        });
    }, 
    remove: function(){
        _.each(this.inputs, function(row){row.remove();});
        this.inputs = [];
        this.$tbody.empty();
    }, 
    redraw: function(vars){
        this.remove();
        if(vars.length <= 0){
            return this.addEmptyInfo();
        }
        for(var i=0, size=vars.length; i<size; i+=2){
            this.addRow(vars[i], vars[i+1]);
        };
    }, 
    addRow: function(left, right){
        var row = new preview.TemplateVarRowView({left:left, right:right});
        this.inputs.push(row);
        this.$tbody.append(row.render().el);
    }, 
    addEmptyInfo: function(){
        var message = "この券面テンプレートには プレースホルダーが設定されていません";
        this.$tbody.append($("<tr>").html(this.emptyInfoTemplate({"message": message})));
    }
});
