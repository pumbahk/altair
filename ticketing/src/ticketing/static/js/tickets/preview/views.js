if (!window.preview)
    window.preview = {}

preview.ParamaterManageView = Backbone.View.extend({
    events: {
        'hover input[name="sx"]': "onChangeSx", 
        'hover input[name="sy"]': "onChangeSy", 
        "change #ticket_format": "onChangeTicketFormat"
    }, 
    initialize: function(opts){
        this.$sx = this.$el.find('input[name="sx"]');
        this.$sy = this.$el.find('input[name="sy"]');
        this.$ticket_format = this.$el.find("#ticket_format");
        // remove it
        this.onChangeTicketFormat();
    }, 
    onChangeTicketFormat: function(){
        this.model.set("ticket_format", {"pk":this.$ticket_format.val(), "name": this.$ticket_format.text()});
    }, 
    onChangeSx: function(){
        this.model.set("sx", this.$sx.val());
    }, 
    onChangeSy: function(){
        this.model.set("sy", this.$sy.val());
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
        this.vms.preview.draw(this.model.get("data"));
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
        this.vms.vars_input.each_input(function($input){
            var k = $input.attr("name");
            if(!!params[k]){
                $input.val(params[k]);
                $input.change();
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
        this.right = opts.right;
    }, 
    render: function(){
        var left = this.template(_.extend(this.left.toJSON(), {position: "left"}));
        var right = ((!!this.right) ? this.template(_.extend(this.right.toJSON(), {position: "right"})) : "");
        this.$el.html(left + right);
        this.$left = this.$el.find(".left");
        this.$right = this.$el.find(".right");
        return this;
    }, 
    onUpdateLeft: function(){ //todo: e.currentTarget ?
        this.left.set("value", this.$el.find("input.left").val());
        // console.log(this.left.toJSON());
    }, 
    onUpdateRight: function(){ //todo: e.currentTarget ?
        this.right.set("value", this.$el.find("input.right").val());
        // console.log(this.right.toJSON());
    }, 
    remove: function(){
        this.left.off();
        this.right.off();
    }
 });
