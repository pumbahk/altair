if (!window.preview)
    window.preview = {}

preview.ParameterManageView = Backbone.View.extend({
    events: {
        'hover input[name="sx"]': "onChangeSx", 
        'hover input[name="sy"]': "onChangeSy", 
        "change #ticket_format": "onChangeTicketFormat", 
    }, 
    initialize: function(opts){
        this.$sx = this.$el.find('input[name="sx"]');
        this.$sy = this.$el.find('input[name="sy"]');
        this.$ticket_format = this.$el.find("#ticket_format");
        // remove it
        this.onChangeTicketFormat();
        this.model.on("change:sx", this.reDrawSx, this);
        this.model.on("change:sy", this.reDrawSy, this);
        this.model.on("*params.ticketformat.update", this.reDrawTicketFormatCandidates, this);
        this.vms = opts.vms;
    }, 
    reDrawTicketFormatCandidates: function(candidates){
        // candidates: [{name: "foo", type: ":sej", pk: "10"}, ...];
        this.vms.ticket_format.redraw(candidates); 
        this.model.changeTicketFormat({"pk": candidates[0] .pk, 
                                       "name": candidates[0].name, 
                                       "type": candidates[0].type.replace(":", "")});
    }, 
    onChangeTicketFormat: function(){
        var name_and_type = this.$ticket_format.find(":selected").text().split(":"); // <ticket_format_name>:<delivery_method_type>
        this.model.changeTicketFormat({"pk":this.$ticket_format.val(),
                                       "name": name_and_type[0],
                                       "type": name_and_type[1]});
        this.model.reDraw();
    }, 
    onChangeSx: function(){
        this.model.set("sx", this.$sx.val());
    }, 
    onChangeSy: function(){
        this.model.set("sy", this.$sy.val());
    }, 
    reDrawSx: function(){
        this.$sx.val(this.model.get("sx"));
    }, 
    reDrawSy: function(){
        this.$sy.val(this.model.get("sy"));
    }
});

preview.SVGFromModelView = Backbone.View.extend({
    // id, model_name -> svg
    events: {"change #model_candidates": "onChangeModel"}, 
    initialize: function(opts){
        this.modelname = opts.modelname;
        if(!this.modelname) throw "modelname is not found";
        this.idname = opts.idname
        if(!this.idname) {this.idname = "model_candidates";}
        this.vms = opts.vms;
    }, 
    onChangeModel: function(){
        var pk = this.$select.val();
        this.model.changeHolder({pk: pk, name: this.modelname}); //params
    }, 
    render: function(label, candidates){
        var $select = $('<select class="inline input">').attr("id", this.idname);
        this.$select = $select;

        _(candidates).each(function(c){
            $select.append($("<option>").text(c.name).attr("value", c.pk));
        });
        this.$el.find(".brand").hide();
        var root = this.$el.find("#subnav .nav");
        root.append($('<li style="margin-left:20px;">').text(label).append($select));
    }
});

preview.ComboboxSVGFromModelView = Backbone.View.extend({
    // id, model_name -> svg
    events: {"change #left_candidates": "onChangeLeft", 
             "change #right_candidates": "onChangeRight", 
            }, 
    initialize: function(opts){
        this.modelname = opts.modelname;
        if(!this.modelname) throw "modelname is not found";
        this.leftIdname = opts.leftIdname
        if(!this.leftIdname) {this.leftIdname = "left_candidates";}
        this.rightIdname = opts.rightIdname
        if(!this.rightIdname) {this.rightIdname = "right_candidates";}
        this.vms = opts.vms;
        this.subCandidates = {}
    }, 
    onChangeRight: function(e, rightName){
        var pk = rightName || this.$rightSelect.val();
        this.model.changeHolder({pk: pk, name: this.modelname}); //params
    }, 
    onChangeLeft: function(){
        var rightName = this.$leftSelect.val();
        var candidates = this.subCandidates[rightName];
        var $right = this.$rightSelect;
        $right.empty();
        _(candidates).each(function(c){
            $right.append($("<option>").text(c.name).attr("value", c.pk));
        });
        if(candidates.length == 1){
            this.onChangeRight(null, candidates[0].pk);
        }
    }, 
    render: function(label, candidates){
        var subCandidates = this.subCandidates = {};
       // [{name: "foo", pk: 1,  candidates:[{name: "bar", pk: 1}, {name: "boo", pk: 2}, ...]}, ...]
        var $leftSelect = this.$leftSelect = $('<select class="inline input-medium">').attr("id", this.leftIdname);
        var $rightSelect = this.$rightSelect = $('<select class="inline input-medium">').attr("id", this.rightIdname);

        _(candidates).each(function(c){
            subCandidates[c.pk] = c.candidates;
            $leftSelect.append($("<option>").text(c.name).attr("value", c.pk));
        });
        _(candidates[0].candidates).each(function(c){
            $rightSelect.append($("<option>").text(c.name).attr("value", c.pk));
        });
        this.$el.find(".brand").hide();
        var root = this.$el.find("#subnav .nav");
        root.append($('<li style="margin-left:20px;">').text(label).append($leftSelect));
        root.append($('<li>').append($rightSelect));
        if(candidates.length == 1){
            this.onChangeLeft(null, candidates[0].pk);
        }
    }
});

preview.Combobox3SVGFromModelView = Backbone.View.extend({
    // id, model_name -> svg
    events: {"change #left_candidates": "onChangeLeft", 
             "change #middle_candidates": "onChangeMiddle", 
             "change #right_candidates": "onChangeRight", 
            }, 
    initialize: function(opts){
        this.modelname = opts.modelname;
        if(!this.modelname) throw "modelname is not found";
        if(!this.leftIdname) {this.leftIdname = "left_candidates";}
        if(!this.middleIdname) {this.middleIdname = "middle_candidates";}
        if(!this.rightIdname) {this.rightIdname = "right_candidates";}
        this.vms = opts.vms;
        this.subCandidates = {}
        this.subsubCandidates = {}
    }, 
    onChangeRight: function(e,rightName){
        var pk = this.$middleSelect.val();
        var sub_pk = rightName || this.$rightSelect.val();
        this.model.changeHolder({pk: pk, name: this.modelname, sub: {pk: sub_pk,  name: "Sub"}}); //params
    }, 
    onChangeLeft: function(e, middleName){
        var middleName = middleName || this.$leftSelect.val();
        var candidates = this.subCandidates[middleName];
        var $right = this.$rightSelect;
        var $middle = this.$middleSelect;
        $right.empty();
        $middle.empty();
        _(candidates).each(function(c){
            $middle.append($("<option>").text(c.name).attr("value", c.pk));
        });
        if(candidates.length == 1){
            this.onChangeMiddle(null, candidates[0].pk);
        }
    }, 
    onChangeMiddle: function(e,rightName){
        var rightName = rightName || this.$middleSelect.val();

        var formatId = this.model.get("ticket_format").pk;
        var candidates = _(this.subsubCandidates[rightName]).filter(function(c){
            return !c.format_id || c.format_id == formatId;
        });

        var $right = this.$rightSelect;
        $right.empty();
        _(candidates).each(function(c){
            $right.append($("<option>").text(c.name).attr("value", c.pk));
        });
        if(candidates.length == 1){
            this.onChangeRight(null, candidates[0].pk);
        }
    }, 
    render: function(label, candidates){
        var subCandidates = this.subCandidates = {};
        var subsubCandidates = this.subsubCandidates = {}
       // [{name: "foo", pk: 1,  candidates:[{name: "bar", pk: 1}, {name: "boo", pk: 2}, ...]}, ...]
        var $leftSelect = this.$leftSelect = $('<select class="inline input-medium">').attr("id", this.leftIdname);
        var $middleSelect = this.$middleSelect = $('<select class="inline input-medium">').attr("id", this.middleIdname);
        var $rightSelect = this.$rightSelect = $('<select class="inline input-medium">').attr("id", this.rightIdname);
        var formatId = this.model.get("ticket_format").pk;

        _(candidates).each(function(c){
            subCandidates[c.pk] = c.candidates;
            _(c.candidates).each(function(cc){
                subsubCandidates[cc.pk]  = cc.candidates;
            });
            $leftSelect.append($("<option>").text(c.name).attr("value", c.pk));
        });
        _(candidates[0].candidates).each(function(c){
            $middleSelect.append($("<option>").text(c.name).attr("value", c.pk));
        });
        _(candidates[0].candidates[0].candidates).each(function(c){
            if(!c.format_id || c.format_id == formatId){
                $rightSelect.append($("<option>").text(c.name).attr("value", c.pk));
            }
        });
        this.$el.find(".brand").hide();
        var root = this.$el.find("#subnav .nav");
        root.append($('<li style="margin-left:20px;">').text(label).append($leftSelect));
        root.append($('<li>').append($middleSelect));
        root.append($('<li>').text("対象チケット").append($rightSelect));
        if(candidates.length == 1){
            this.onChangeLeft(null, candidates[0].pk);
        }
    }
});


preview.DragAndDropSVGSupportView = Backbone.View.extend({
  initialize: function(opts){
      this.vms = opts.vms || {}
      var compose = preview.DragAndDropSupportService.compose;
      var default_action_cancel = preview.DragAndDropSupportService.cancel;
      
      this.el.addEventListener("dragenter", default_action_cancel, false);
      this.el.addEventListener('dragover',  compose(default_action_cancel, this.vms.droparea.touched.bind(this.vms.droparea)), false);
      this.el.addEventListener('dragleave', compose(default_action_cancel, this.vms.droparea.untouched.bind(this.vms.droparea)), false);
      this.el.addEventListener('drop',
                               compose(default_action_cancel,
                                       this.vms.droparea.untouched.bind(this.vms.droparea), 
                                       preview.DragAndDropSupportService.onDrop(this.onLoadSVG.bind(this))),
                               false);
  }, 
  _onLoadSVGPassed: function(svg){
      this.vms.spinner.loading();
      return this.model.updateToRaw(svg);
  }, 
  onLoadSVG: function(e){
      return this._onLoadSVGPassed(e.target.result)
  }
});

preview.PreviewImageView = Backbone.View.extend({
    events: {
        "click #preview_area img#preview_img": "reDrawImage"
    }, 
    initialize: function(opts){
        this.model.on("*preview.update.loading", this.onLoading, this);
        this.model.on("*preview.update.cancel", this.onCancel, this);
        this.model.on("*preview.update.rendering", this.onRendering, this);
        this.model.on("*preview.resize", this.onResizing, this);
        this.vms = opts.vms;
    }, 
    reDrawImage: function(){
        this.model.reDraw();
    }, 
    onLoading: function(){
        this.vms.spinner.loading();
    }, 
    onCancel: function(){
        this.vms.spinner.noloading();
    }, 
    onRendering: function(){
        this.vms.preview.draw(this.model.get("data"), this.model.get("rendering_width"), this.model.get("rendering_height"));
        this.vms.spinner.noloading();
    }, 
    onResizing: function(){
        this.vms.preview.resize(this.model.get("rendering_width"), this.model.get("rendering_height"));
        this.vms.spinner.noloading();
    }
});

preview.TemplateFillValuesView = Backbone.View.extend({
    events: {
        "click a#redraw_btn": "onRedrawBtnClick"
    }, 
    initialize: function(opts){
        this.model.on("*vars.update.vars", this.onUpdateTemplateVars, this);
        this.vms = opts.vms;
    }, 
    // user action
    onRedrawBtnClick: function(){
        this.model.commitVarsValues();
    }, 
    // model -> view
    onUpdateTemplateVars: function(){
        this.vms.vars_input.redraw(this.model.get("vars").models);
    }, 
    // api
    fillsVarsWithParams: function(params){
        this.vms.vars_input.each_input(function($input, model){
            var k = $input.attr("name");
            if(!!params[k]){
                model.set("value", params[k]);
            }
        });
    }
});

preview.TemplateVarRowView = Backbone.View.extend({
    tagName: "tr", 
    className: "vars-row", 
    template: _.template('<td><%- name %></td><td><input class="<%- position%>" name="<%- name %>" value="<%- value %>" placeholder="ここに文字を入力してください"></input></td>'), 
    events: {
        "change input.left": "onUpdateLeft", 
        "change input.right": "onUpdateRight", 
    }, 
    initialize: function(opts){
        this.left = opts.left;
        if(!this.left) throw "opts.left is not found";
        this.left.on("change", this.reDrawLeft, this)
        if(!!opts.right){
            this.right = opts.right;
            this.right.on("change", this.reDrawRight, this);
        }
    }, 
    render: function(){
        var left = this.template(_.extend(this.left.toJSON(), {position: "left"}));
        var right = ((!!this.right) ? this.template(_.extend(this.right.toJSON(), {position: "right"})) : "");
        this.$el.html(left + right);
        this.$left = this.$el.find(".left");
        this.$right = this.$el.find(".right");
        return this;
    }, 
    reDrawLeft: function(){
        this.$left.val(this.left.get("value"));
    }, 
    reDrawRight: function(){
        this.$right.val(this.right.get("value"))
    }, 
    onUpdateLeft: function(){ //todo: e.currentTarget ?
        this.left.set("value", this.$el.find("input.left").val());
    }, 
    onUpdateRight: function(){ //todo: e.currentTarget ?
        this.right.set("value", this.$el.find("input.right").val());
    }, 
    remove: function(){
        this.left.off();
        if(!!this.right){
            this.right.off();
        }
    }
 });
