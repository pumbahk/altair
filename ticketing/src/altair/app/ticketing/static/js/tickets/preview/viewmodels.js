if (!window.preview)
    window.preview = {};

preview.CandidateCollectionViewModel = core.ViewModel.extend({
    initialize: function(id,className){
        this.id = id;
        this.$el = $('<select class="inline">').addClass(className).attr("id", id);
        this.candidates = [];
        this.models = {};
        this.children = {};
        this.i = 0;
    },
    addModel: function(vm){
        this.candidates[this.i] = vm;
        this.models[vm.pk] = vm;    //viewmodel.pk == viewmodel.model.get("pk")
        this.i += 1;
    },
    addChild: function(k,val){
        this.children[k] = val;
    },
    getChild: function(k){
        return this.children[k];
    },
    exactCandidates: function(filter_id){
        var arr = [];
        if(!!filter_id){
            _(this.candidates).each(function(vm){
                if(vm.model.get("format_id") == filter_id)
                    arr.push(vm);
            });
        } else {
            _(this.candidates).each(function(vm){
                arr.push(vm);
            });
        }
        return arr
    },
    render: function(filter_id){
        var $el = this.$el;
        _(this.exactCandidates()).each(function(vm){
            $el.append(vm.render());
        });
        return $el;
    }
});


preview.ResourceViewModel = core.ViewModel.extend({
    initialize: function(model, className){
        this.model = model;
        this.pk = model.get("pk");
        this.$el = $('<option>');
    },
    render: function(){
        this.$el.text(this.model.get("label")).attr("value", this.pk);
        return this.$el;
    }
});


preview.PreviewImageViewModel = core.ViewModel.extend({
    draw: function(imgdata, width, height){
        this.$el.empty();
        var preview_img = $('<img id="preview_img" title="clickして再描画" alt="clickして再描画">').attr('src', imgdata);
        if(!!width){preview_img.width(core.UnitCalcService.convert(width));}
        if(!!height){preview_img.height(core.UnitCalcService.convert(height));}
        this.$el.append(preview_img);
        this.$el.parents(".empty").removeClass("empty");
    }, 
    resize: function(width, height){
        var $img = this.$el.find("img#preview_img");
        $img.width(core.UnitCalcService.convert(width));
        $img.height(core.UnitCalcService.convert(height));
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

preview.SelectCandidatesViewModel = core.ViewModel.extend({
    template: _.template(
        '<% _.each(iterable, function(d){%><option data-preview="<%= d.type %>" value="<%= d.pk %>"><%= d.name %>:<%= d.type %></option><%});%>'
    ),
    redraw: function(candidates){
        this.$el.html(this.template({iterable: candidates}));
    },
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
