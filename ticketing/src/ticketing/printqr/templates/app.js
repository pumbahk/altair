// model
var DataStore = Backbone.Model.extend({
  defaults: {
    ordered_product_item_token_id:  null, 
    printer_name: null, 
    ticket_template_name: null, 
    ticket_template_id: null, 
    page_format_name: null, 
    page_format_id: null, 
    printed: false, 

    qrcode_status: "preload", 
    qrcode: null, 
    
    orderno: null,
    performance: null,
    product: null,
  }, 
  updateByQRData: function(data){
    // this order is important for call api.applet.ticket.data(ordered_product_item_token_id, printed)
    this.set("ordered_product_item_token_id", data.ordered_product_item_token_id);
    this.set("orderno", data.orderno);
    this.set("performance", data.performance_name+" -- "+data.performance_date);
    this.set("product", data.product_name+"("+data.seat_name+")");

    if(!!(data.printed)){
      this.set("printed", true);
      this.trigger("*qr.printed.already");
    } else {
      this.set("printed", false);
      this.trigger("*qr.not.printed");
    }
  }
});

// view
var DataStoreDescriptionView = Backbone.View.extend({
  initialize: function(){
    this.model.bind("change:qrcode_status", this.showQrcodeStatus, this);
    this.model.bind("change:orderno", this.showOrderno, this);
    this.model.bind("change:performance", this.showPerformance, this);
    this.model.bind("change:product", this.showProduct, this);
    this.model.bind("change:printer_name", this.showPrinter, this);
    this.model.bind("change:page_format_name", this.showPageFormat, this);
    this.model.bind("change:ticket_template_name", this.showTicketTemplate, this);
    this.model.bind("refresh", this.refresh, this);

    this.$qrcode_status = this.$el.find("#desc_qrcode_status");
    this.$orderno = this.$el.find("#desc_orderno");
    this.$performance = this.$el.find("#desc_performance");
    this.$product = this.$el.find("#desc_product");
    this.$printer = this.$el.find("#desc_printer");
    this.$ticket_template = this.$el.find("#desc_ticket_template");
    this.$page_format = this.$el.find("#desc_page_format");
  }, 
  showQrcodeStatus: function(){
    this.$qrcode_status.text(this.model.get("qrcode_status"));
  }, 
  showOrderno: function(){
    this.$orderno.text(this.model.get("orderno"));
  }, 
  showPerformance: function(){
    this.$performance.text(this.model.get("performance"));
  }, 
  showProduct: function(){
    this.$product.text(this.model.get("product"));
  }, 
  showPrinter: function(){
    this.$printer.text(this.model.get("printer_name"));
  }, 
  showTicketTemplate: function(){
    this.$ticket_template.text(this.model.get("ticket_template_name"));
  }, 
  showPageFormat: function(){
    this.$page_format.text(this.model.get("page_format_name"));
  }, 
  refresh: function(){
    this.$orderno.text("");
    this.$performance.text("");
    this.$product.text("");
  }
});


var MessageView = Backbone.View.extend({
  initialize: function(){
    this.$alert = this.$el.find("#alert_message");
    this.$info = this.$el.find("#info_message");
    this.$error = this.$el.find("#error_message");
    this.$success = this.$el.find("#success_message");
    this.$messages = this.$el.find(".alert");
  }, 
  _clear: function(){
    this.$messages.hide();
  }, 
  alert: function(message){
    this._clear();
    this.$alert.text(message).show();
  }, 
  info: function(message){
    this._clear();
    this.$info.text(message).show();
  }, 
  error: function(message){
    this._clear();
    this.$error.text(message).show();
  }, 
  success: function(message){
    this._clear();
    this.$success.text(message).show();
  }
});

var AppPageViewBase = Backbone.View.extend({
  initialize: function(opts){
    this.apiResource = opts.apiResource;
    this.messageView = opts.messageView;
    this.router = opts.router;
    this.datastore = opts.datastore;
    this.nextView = null;
  }, 
  focusNextPage: function(){
    this.router.navigate(this.nextView.$el.attr("id"), true);
  }
});

var QRInputView = AppPageViewBase.extend({
  events: {
    "click #load_button": "loadQRSigned", 
    "keypress input[name='qrcode']": "readOnEnter"
  }, 
  initialize: function(opts){
    QRInputView.__super__.initialize.call(this, opts);
    this.$qrcode = this.$el.find('input[name="qrcode"]')
    this.$status = this.$el.find('#status')
    this.datastore.bind("change:qrcode_status", this.showStatus, this);
    this.datastore.bind("*qr.printed.already", this.notifyPrintedAlready, this);
  }, 
  notifyPrintedAlready: function(){
    this.messageView.alert("既にそのチケットは印刷されてます");
  }, 
  showStatus: function(){
    this.$status.text(this.datastore.get("qrcode_status"));
  }, 
  readOnEnter: function(e){
    // if Enter key is typed then call `loadQRSigned'
    if(e.keyCode == 13){
      this.loadQRSigned().always(function(){this.$qrcode.val("");}.bind(this));
    }
  }, 
  loadQRSigned: function(){
    var url = this.apiResource["api.ticket.data"];
    var self = this;
    return $.getJSON(url, {qrsigned: this.$qrcode.val()})
      .done(function(data){
        self.messageView.success("QRコードからデータが読み込めました");
        self.datastore.set("qrcode_status", "loaded");
        self.datastore.updateByQRData(data);
        self.nextView.drawTicketInfo(data);
        setTimeout(function(){self.focusNextPage();}, 1)
        return data;})
      .fail(function(s, err){
        self.messageView.error("うまくQRコードを読み込むことができませんでした:");
        self.datastore.set("qrcode_status", "fail");
        self.datastore.trigger("refresh");
      });
  } 
});

var TicketInfoView = AppPageViewBase.extend({
  initialize: function(opts){
    TicketInfoView.__super__.initialize.call(this, opts);

    this.$user = this.$el.find("#user");
    this.$codeno = this.$el.find("#codeno");
    this.$orderno = this.$el.find("#orderno");
    this.$performanceName = this.$el.find("#performance_name");
    this.$performanceDate = this.$el.find("#performance_date");
    this.$product_name = this.$el.find("#product_name");
    this.$seatno = this.$el.find("#seatno");
  }, 
  drawTicketInfo: function(data){
    //console.dir(data);
    this.$user.text(data.user);
    this.$codeno.text(data.codeno);
    this.$orderno.text(data.orderno);
    this.$performanceDate.text(data.performance_date);
    this.$performanceName.text(data.performance_name);
    this.$product_name.text(data.product_name);
    this.$seatno.text(data.seat_name);  
  }
});

var FormatChoiceView = AppPageViewBase.extend({
  events:{
    "change #printer input": "printerSettingsChanged", 
    "change #ticket_template input": "ticketTemplateSettingsChanged", 
    "change #page_format input": "pageFormatChanged"
  }, 
  initialize: function(opts){
    FormatChoiceView.__super__.initialize.call(this, opts);
    this.printers = null;
    this.templates = null;
    this.$printer = this.$el.find("#printer");
    this.$ticketTemplate = this.$el.find("#ticket_template");
    this.$pageFormat = this.$el.find("#page_format")
  }, 
  printerSettingsChanged: function(){
    var printer_name = this.$printer.find("input:checked").val();
    this.datastore.set("printer_name", printer_name);
  },
  ticketTemplateSettingsChanged: function(){
    var ticket_template = this.$ticketTemplate.find("input:checked");
    this.datastore.set("ticket_template_name", ticket_template.attr("data-name"));
    this.datastore.set("ticket_template_id", ticket_template.val());
  }, 
  pageFormatChanged: function(){
    var page_format = this.$pageFormat.find("input:checked");
    this.datastore.set("page_format_name", page_format.attr("data-name"));
    this.datastore.set("page_format_id", page_format.val());
  }, 
  redrawPrinterArea: function(printers){
    this.printers = printers;
    var targetArea = this.$printer;
    targetArea.empty();
    for(var i = printers.iterator(); i.hasNext();){
      var printer = i.next();
      var e = $('<div class="control-group">');
      e.append($('<span>').text(printer.getName()+": "));
      e.append($('<input type="radio" name="printer">').attr("value", printer.getName()));
      targetArea.append(e);
    }
  }, 
  redrawTicketTemplateArea: function(templates){
    var targetArea = this.$ticketTemplate;
    targetArea.empty()
    for(var i = templates.iterator(); i.hasNext();){
      var template = i.next();
      var e = $('<div class="control-group">');
      e.append($('<span>').text(template.getName()+": "));
      e.append($('<input type="radio" name="tickettemplate">')
               .attr("value", template.getId())
               .attr("data-name", template.getName()));
      targetArea.append(e);
    }
  }, 
  redrawPageFormatArea: function(pageformats){
    var targetArea = this.$pageFormat;
    targetArea.empty()
    for(var i = pageformats.iterator(); i.hasNext();){
      var pageformat = i.next();
      var e = $('<div class="control-group">');
      e.append($('<span>').text(pageformat.getName()+": "));
      e.append($('<input type="radio" name="pageformat">')
               .attr("value", pageformat.getId())
               .attr("data-name", pageformat.getName()));
      targetArea.append(e);
    }
  }
});

var PrintConfirmView = AppPageViewBase.extend({
  events: {
    "click #print_button": "clickPrintButton"
  }, 
  initialize: function(opts){
    PrintConfirmView.__super__.initialize.call(this, opts);
  }, 
  _validationPrePrint: function(){
    if(this.datastore.get("ticket_template_id") == null){
      this.messageView.alert("チケットテンプレートが設定されていません")
      return false;
    }
    if(this.datastore.get("page_format_id") == null){
      this.messageView.alert("ページフォーマットが設定されていません");
      return false;
    }
    if(this.datastore.get("printer_name") == null){
      this.messageView.alert("プリンタが設定されていません");
      return false;
    }
    return true;
  }, 
  clickPrintButton: function(){
    if(!this._validationPrePrint()){
      return;
    }
    if(this.datastore.get("printed")){
      this.messageView.alert("既に印刷済みです。");
    }else{
      this.datastore.set("printed", true);
    }
  }
});

var AppletView = Backbone.View.extend({
  initialize: function(opts){
    this.appviews = opts.appviews;
    this.datastore = opts.datastore;
    this.service = opts.service;
    this.createProxy = opts.createProxy;
    this.apiResource = opts.apiResource;
    this.datastore.bind("*qr.not.printed", this.createTicket, this);
    this.datastore.bind("change:ordered_product_item_token_id", this.fetchPinterCandidates, this); //eliminate call times:
    this.datastore.bind("change:ordered_product_item_token_id", this.fetchTemplateCandidates, this); //eliminate call times:
    this.datastore.bind("change:ordered_product_item_token_id", this.fetchPageFormatCandidates, this); //eliminate call times:

    this.datastore.bind("change:printer_name", this.setPrinter, this);
    this.datastore.bind("change:ticket_template_id", this.setTicketTemplate, this);
    this.datastore.bind("change:page_format_id", this.setPageFormat, this);

    this.datastore.bind("change:printed", this.sendPrintSignalIfNeed, this);
  }, 
  sendPrintSignalIfNeed: function(){
    if(this.datastore.get("printed")){
      try {
        this.service.printAll();
        this.appviews.messageView.success("チケット印刷できました。");
      } catch (e) {
        this.appviews.messageView.error(e);
      }
    }
  }, 
  setPrinter: function(){ //liner
    var printer_name = this.datastore.get("printer_name");
    var printers = this.service.getPrintServices();
    for(var i = printers.iterator(); i.hasNext();){
      var printer = i.next();
      if(printer.getName() == printer_name){
        this.service.setPrintService(printer);
      }
    }
  }, 
  setTicketTemplate: function(){ //liner
    var template_id = this.datastore.get("ticket_template_id");
    var ticketTemplates = this.service.getTicketTemplates();
    for(var i = ticketTemplates.iterator(); i.hasNext();){
      var template = i.next();
      if(template.getId() == template_id){
        this.service.setTicketTemplate(template);
      }
    }
  }, 
  setPageFormat: function(){ //liner
    var page_format_id = this.datastore.get("page_format_id");
    var pageFormats = this.service.getPageFormats();
    for(var i = pageFormats.iterator(); i.hasNext();){
      var page_format = i.next();
      if(page_format.getId() == page_format_id){
        this.service.setPageFormat(page_format);
      }
    }
  }, 
  createTicket: function(){
    var tokenId = this.datastore.get("ordered_product_item_token_id");
    var self = this;
    $.ajax({
      type: 'POST',
      processData: false,
      data: JSON.stringify({ ordered_product_item_token_id: tokenId }),
      contentType: 'application/json',
      dataType: 'json',
      url: this.apiResource["api.ticketdata_from_token_id"]
    }).done(function (data) {
      if (data['status'] != 'success') {
        self.appviews.messageView.alert(data['message']);
        return;
      }
      self.appviews.messageView.success("券面データが保存されました");
      $.each(data['data'], function (_, ticket) {
        self.service.addTicket(self.service.createTicketFromJSObject(ticket));
      });
    }).fail(function(msg){self.appviews.messageView.alert(msg)});
  }, 
  fetchPinterCandidates: function(){
    var printers = this.service.getPrintServices();
    this.appviews.three.redrawPrinterArea(printers);
  }, 
  fetchTemplateCandidates: function(){
    var ticketTemplates = this.service.getTicketTemplates();
    this.appviews.three.redrawTicketTemplateArea(ticketTemplates);
  }, 
  fetchPageFormatCandidates: function(){
    var pageFormats = this.service.getPageFormats();
    this.appviews.three.redrawPageFormatArea(pageFormats);
  }
});

var AppRouter = Backbone.Router.extend({
  routes: {
    ":page": "show_page"
  }, 
  show_page:  function(page){
    $(".onepage").hide();
    $(".onepage#{0}".replace("{0}", page)).show();
    $("#tabbar #tab_{0}".replace("{0}", page)).tab("show"); //bootstrap
    
    // tooooooooooooooooo ad-hoc
    if(page == "one"){
      var $qrinput = $("#one input[name='qrcode']");
      $qrinput.focus();
    }
  }, 
  start: function(){
    var self = this;
    $("a[href^=#]").on("click",  function(e){
      self.navigate($(this).attr("href").substr(1), true);
      e.preventDefault();
    });
    self.navigate("one", true);
  }
})
