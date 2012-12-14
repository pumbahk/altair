if (!window.preview)
    window.preview = {};

preview.ApiCommunicationGateway = core.ApiCommunicationGateway.extend({
    initialize: function(opts){
        this.message = opts.message;
        this.preview = this.models.preview;
        this.svg = this.models.svg;
        this.vars = this.models.vars;
        this.params = this.models.params;

        this.svg.on("*svg.update.raw", this.svgRawToX, this);
        this.svg.on("*svg.update.normalize", this.svgNormalizeToX, this);
        this.svg.on("*svg.update.normalize", this.collectTemplateVars, this);
        this.svg.on("*svg.update.filled", this.svgFilledToX, this);

        this.vars.on("*vars.commit.vars", this.commitVarsValues, this);

        this.preview.on("*preview.redraw",  this.previewReDraw, this);
    }, 
    _apiFail: function(s, err){
        this.message.error(s.responseText);
        this.preview.cancelRendering();
    }, 
    previewReDraw: function(){
        this.vars.commitVarsValues();
    }, 
    commitVarsValues: function(vars_values){
        var self = this;
        if(!this.svg.get("normalize")){
            this.message.alert("まだ券面テンプレートをuploadしていません。券面テンプレートをDrag&Dropしてください")
            return;
        }
        self.message.info("プレースホルダーに値を挿入しています....");
        return $.post(this.apis.fillvalues, {"svg": this.svg.get("normalize"), "params": JSON.stringify(vars_values)})
            .pipe(core.ApiService.rejectIfStatusFail(function(data){
                self.svg.updateToFilled(data.data);
                self.message.info("プレースホルダーに値が挿入されました");
            }))
            .fail(this._apiFail.bind(this));
    }, 
    svgRawToX: function(){
        this.preview.beforeRendering();
        var self = this;
        self.message.info("券面テンプレートを正規化しています....");
        return $.post(this.apis.normalize, {"svg": this.svg.get("data")})
            .pipe(core.ApiService.rejectIfStatusFail(function(data){
                self.svg.updateToNormalize(data.data);
                self.message.info("券面テンプレートを正規化しました");
            }))
            .fail(this._apiFail.bind(this));
    }, 
    svgNormalizeToX: function(){
        this.preview.beforeRendering();
        var self = this;
        self.message.info("preview画像がレンダリングしています....");
        var params = {"svg": this.svg.get("data"), 
                      ticket_format: this.params.get("ticket_format").pk};
        return $.post(this.apis.previewbase64, params)
            .pipe(core.ApiService.rejectIfStatusFail(function(data){
                self.preview.startRendering("data:image/png;base64,"+data.data); //add-hoc
                self.message.info("preview画像がレンダリングされました");
            }))
            .fail(this._apiFail.bind(this));
    }, 
    svgFilledToX: function(){
        var self = this;
        this.preview.beforeRendering();
        self.message.info("preview画像がレンダリングしています....");
        var params = {svg: this.svg.get("data"),
                      sx: this.params.get("sx"),
                      sy: this.params.get("sy"), 
                      ticket_format: this.params.get("ticket_format").pk};
        return $.post(this.apis.previewbase64, params)
            .pipe(core.ApiService.rejectIfStatusFail(function(data){
                self.preview.startRendering("data:image/png;base64,"+data.data); //add-hoc
                self.message.info("preview画像がレンダリングされました");
            }))
            .fail(this._apiFail.bind(this));
    }, 
    collectTemplateVars: function(){ // todo:move it?
        var self = this;
        self.message.info("券面テンプレートからプレースホルダーを抽出しています....");
        $.post(this.apis.collectvars, {"svg": this.models.svg.get("normalize")})
            .pipe(core.ApiService.rejectIfStatusFail(function(data){
                self.vars.updateVars(data.data);
                self.message.info("券面テンプレートからプレースホルダーを抽出しました");
            }))
            .fail(this._apiFail.bind(this));
    }
});
