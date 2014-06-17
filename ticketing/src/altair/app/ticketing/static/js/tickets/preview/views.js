if (!window.preview)
    window.preview = {};

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
        this.model.on("*params.ticket_format.recreate", this.reDrawTicketFormatCandidates, this);
        this.vms = opts.vms;
    }, 
    reDrawTicketFormatCandidates: function(candidates, preview_type, ticket_format){
        // candidates: [{name: "foo", type: ":sej", pk: "10"}, ...];
        this.vms.ticket_format.redraw(candidates); 
        if(!!ticket_format){
            this.model.changePreviewType(ticket_format.type);
            this.model.changeTicketFormat(ticket_format);
        }else{
            if(!!preview_type){
                this.model.changePreviewType(preview_type);
            }
            this.model.changeTicketFormat({"pk": candidates[0].pk, 
                                           "name": candidates[0].name, 
                                           "type": candidates[0].type});
        }
    },
    onChangeTicketFormat: function(){
        var $option = this.$ticket_format.find(":selected");
        var name = $option.text();
        var value = $option.val();
        if(!!name){
            var preview_type = $option.data("preview");
            this.model.changePreviewType(preview_type);
            this.model.changeTicketFormat({"pk":value, "name": name});
            this.model.reDraw();
        }
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
        this.idname = opts.idname;
        if(!this.idname) {this.idname = "model_candidates";}
        this.vms = opts.vms;
    }, 
    onChangeModel: function(){
        var pk = this.$select.val();
        this.model.changeHolder({pk: pk, name: this.modelname}); //params
    }, 
    createSelect: function(candidates){
        var $select = $('<select class="inline input">').attr("id", this.idname);
        this.$select = $select;

        _(candidates).each(function(c){
            $select.append($("<option>").text(c.name).attr("value", c.pk));
        });
        return $select;
    },
    update: function(label, candidates){
        var $select = this.createSelect(candidates);
        $("#"+this.idname).parent().remove();
        var root = this.$el.find("#subnav .nav");
        root.append($('<li style="margin-left:20px;">').text(label).append($select));
    },
    render: function(label, candidates){
        var $select = this.createSelect(candidates);
        this.$el.find(".brand").hide();
        var root = this.$el.find("#subnav .nav");
        root.append($('<li style="margin-left:20px;">').text(label).append($select));
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
        this.model.on("*params.ticket_format.update", this.onChangeFormat, this);
    }, 
    onChangeRight: function(e,middleVal, rightVal, silent){
        var pk = middleVal || this.middle.$el.val();
        var sub_pk = rightVal || this.right.$el.val();
        if(this.right.models[sub_pk].model && this.right.models[sub_pk].model.hasTicketFormats()){
            this.model.trigger("*params.ticket_format.restriction", this.right.models[sub_pk].model);
        }
        this.model.changeHolder({pk: pk, name: this.modelname, sub: {pk: sub_pk,  name: "Sub"}}, silent); //params
    }, 
    onChangeFormat: function(){
        return this.onChangeMiddle(null, null, true);
    },
    onChangeLeft: function(e, leftVal, silent){
        leftVal = leftVal || this.left.$el.val();
        if(this.left.models[leftVal].model && this.left.models[leftVal].model.hasTicketFormats()){
            this.model.trigger("*params.ticket_format.restriction", this.left.models[leftVal].model);
        }
        this.middle = this.left.getChild(leftVal);
        this.$middleWrapper.html(this.middle.render());
        if(this.middle.candidates.length == 1){
            this.onChangeMiddle(null, this.middle.candidates[0].pk, silent);
        }
    }, 
    onChangeMiddle: function(e,middleVal){
        middleVal = middleVal || this.middle.$el.val();
        this.right = this.middle.getChild(middleVal);
        if(this.middle.models[middleVal].model && this.middle.models[middleVal].model.hasTicketFormats()){
            this.model.trigger("*params.ticket_format.restriction", this.middles[middleVal].model);
        }
        var filterId = this.model.get("ticket_format").pk;
        this.$rightWrapper.html(this.right.render(filterId));
        var candidates = this.right.exactCandidates(filterId);
        if(candidates.length == 1){
            this.onChangeRight(null, middleVal, candidates[0].pk);
        }
    },
    settingChildren: function(candidates){
        this.left = null;
        this.middle = null;
        this.right = null;
        _(candidates).each(function(c){
            var left = new preview.CandidateCollectionViewModel(this.leftIdname, "input-medium");
            if(!this.left){
                this.left = left;
            }
            // left setting
            left.addModel(
                new preview.ResourceViewModel(
                    new preview.Resource({label: c.name, pk: c.pk, ticket_formats: (c.ticket_formats || [])})));

            // middle setting
            var middle = new preview.CandidateCollectionViewModel(this.middleIdname, "input-medium");
            if(!this.middle){
                this.middle = middle;
            }
            left.addChild(c.pk, middle);

            _(c.candidates).each(function(subc){
                middle.addModel(
                    new preview.ResourceViewModel(
                        new preview.Resource({label: subc.name, pk: subc.pk, ticket_formats: (subc.ticket_formats || [])})));

                // right setting
                var right = new preview.CandidateCollectionViewModel(this.rightIdname, "input-medium");
                if(!this.right){
                    this.right = right;
                }
                middle.addChild(subc.pk, right);
                _(subc.candidates).each(function(subsubc){
                    right.addModel(
                        new preview.ResourceViewModel(
                            new preview.Resource({label: subsubc.name, pk: subsubc.pk, format_id: subsubc.format_id, ticket_formats: (subsubc.ticket_formats || [])})));
                }.bind(this));
            }.bind(this));
        }.bind(this));
    },
    render: function(label, candidates){
        this.settingChildren(candidates);

        this.$el.find(".brand").hide();
        var root = this.$el.find("#subnav .nav");
        this.$leftWrapper = $('<li style="margin-left:20px;">').text(label).append(this.left.render());
        this.$middleWrapper = $('<li>').append(this.middle.render());
        this.$rightWrapper = $('<li>').text("対象チケット").append(this.right.render());
        root.append(this.$leftWrapper);
        root.append(this.$middleWrapper);
        root.append(this.$rightWrapper);
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
