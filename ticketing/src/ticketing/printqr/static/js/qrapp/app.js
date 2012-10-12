// model
var DataStore = Backbone.Model.extend({
  defaults: {
    qrcode_status: "preload", 
    qrcode: null,    
    canceled: false, 

    ordered_product_item_token_id:  null, 
    ordered_product_item_id:  null, 
    printed: false, 
    orderno: null,

    event_id: "*", 
    printer_name: null, 
    ticket_template_name: null, 
    ticket_template_id: null, 
    order_id: null, 
    seat_id: null, 
    page_format_name: null, 
    page_format_id: null, 

    performance: null,
    product: null,
  }, 
  updateByQRData: function(data){
    // this order is important for call api.applet.ticket.data(ordered_product_item_token_id, printed)

    // initialize
    this.set("printed", false);
    this.set("canceled", false);

    // important data
    this.set("ordered_product_item_token_id", data.ordered_product_item_token_id); //order: ordered_product_item_token_id, printed
    this.set("ordered_product_item_id", data.ordered_product_item_id);
    this.set("event_id",  data.event_id);
    this.set("order_id", data.order_id);
    this.set("seat_id", data.seat_id);

    // description data
    this.set("orderno", data.orderno);
    this.set("performance", data.performance_name+" -- "+data.performance_date);
    this.set("product", data.product_name+"("+data.seat_name+")");

    if(!!(data.printed)){
      this.set("qrcode_status", "printed"); //order: qrcode_status ,  printed
      this.set("printed", data.printed);
      this.trigger("*qr.printed.already");
    } else if(data.canceled){
      this.set("qrcode_status", "canceled")
      this.set("canceled", data.canceled);
      this.set("printed", data.printed);
      this.trigger("*qr.canceled.ticket")
    }else {
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
    this.model.bind("*refresh", this.refresh, this);

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
  events: {
    "click #printed_at_force_refresh": "sendRefreshPrintedStatusSignal", 
    "click #canceled_force_print": "sendCanceledForcePrintSignal"
  }, 
  sendRefreshPrintedStatusSignal: function(){
    if(!!(this.refreshCallback && window.confirm("本当に強制再発券ますか？"))){
      this.refreshCallback();
      this.refreshCallback = false;
    }
  }, 
  sendCanceledForcePrintSignal: function(){
    if(!!(this.canceledCallback && window.confirm("本当に強制発券しますか？"))){
      this.canceledCallback();
      this.canceledCallback = false;
    }
  }, 
  initialize: function(){
    this.refreshCallback = false;
    this.canceledCallback = false;
    this.$alert = this.$el.find("#alert_message");
    this.$info = this.$el.find("#info_message");
    this.$error = this.$el.find("#error_message");
    this.$success = this.$el.find("#success_message");
    this.$messages = this.$el.find(".alert");
  }, 
  _clear: function(){
    this.$messages.hide();
  }, 
  alert: function(message, forcehtml){
    this._clear();
    var updator = !!(forcehtml)? this.$alert.html : this.$alert.text;
    updator.call(this.$alert, message).show();
  }, 
  info: function(message, forcehtml){
    this._clear();
    var updator = !!(forcehtml)? this.$info.html : this.$info.text;
    updator.call(this.$info, message).show();
  }, 
  error: function(message, forcehtml){
    this._clear();
    var updator = !!(forcehtml)? this.$error.html : this.$error.text;
    updator.call(this.$error, message).show();
  }, 
  success: function(message, forcehtml){
    this._clear();
    var updator = !!(forcehtml)? this.$success.html : this.$success.text;
    updator.call(this.$success, message).show();
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
    "click #load_button": "loadQRCodeInput", 
    "click #clear_button": "clearQRCodeInput", 
    "keypress input[name='qrcode']": "readOnEnter"
  }, 
  initialize: function(opts){
    QRInputView.__super__.initialize.call(this, opts);
    this.$qrcode = this.$el.find('input[name="qrcode"]')
    this.$status = this.$el.find('#status')
    this.datastore.bind("change:qrcode_status", this.showStatus, this);
    this.datastore.bind("*qr.canceled.ticket", this.notifyMessageForCanceled, this);
    this.datastore.bind("*qr.printed.already", this.notifyMessageForPrintedAlready, this);
    this.datastore.bind("*qr.not.printed", this.focusNextPage, this);

    this.communicating = false;
  }, 
  notifyMessageForPrintedAlready: function(){
    var fmt = 'そのチケットは既に印刷されてます(前回印刷日時:{0}) -- 強制発券しますか？<a id="{1}" class="btn">強制発券する</a>';
    this.messageView.refreshCallback = this.refreshPrintedStatus.bind(this);
    this.messageView.alert(fmt.replace("{0}", this.datastore.get("printed"))
                              .replace("{1}", "printed_at_force_refresh") //see: messagView.events
                            ,  true);
  }, 
  refreshPrintedStatus: function(){
    var params = {
      "ordered_product_item_token_id": this.datastore.get("ordered_product_item_token_id"), 
      "order_no": this.datastore.get("orderno")
    };
    var self = this;
    return $.ajax({
      type: "POST", 
      processData: false, 
      data: JSON.stringify(params), 
      contentType: 'application/json',
      dataType: 'json',
      url: this.apiResource["api.ticket.refresh.printed_status"]
    }).done(function(data){
      if (data['status'] != 'success') {
        self.messageView.error(data['message']);
        return;
      }
      self.datastore.set("printed", false);
      self.messageView.success("チケットを再発券可能にしました");

      // log
      var message = "*qrlog* refresh printed_at order={0} token={1}"
        .replace("{0}", self.datastore.get("order_id"))
        .replace("{1}", self.datastore.get("ordered_product_item_token_id"))
      $.post(self.apiResource["api.log"], {"log": message})

      self._loadQRCodeInput(self.$qrcode.val());
    }).fail(function(s, msg){self.messageView.error(s.responseText)});
  }, 
  notifyMessageForCanceled: function(){
    var fmt = 'そのチケットはキャンセルされています(キャンセルされた日付:{0}) -- 強制発券しますか？<a id="{1}" class="btn">強制発券する</a>';
    this.messageView.canceledCallback = this.refreshCanceled.bind(this);
    this.messageView.alert(fmt.replace("{0}", this.datastore.get("canceled"))
                              .replace("{1}", "canceled_force_print") //see: messagView.events
                            ,  true);
  }, 
  refreshCanceled: function(){
    this.datastore.set("canceled", false);
    this.datastore.set("qrcode_status", "canceld(but force print)")
    this.messageView.success("（キャンセルされたチケットなど本来印刷できない）チケットを印刷できるようにしました。")

    // log
    var message = "*qrlog* canceled ticket force print order={0} token={1}"
      .replace("{0}", this.datastore.get("order_id"))
      .replace("{1}", this.datastore.get("ordered_product_item_token_id"))
    $.post(this.apiResource["api.log"], {"log": message})

    this.focusNextPage();
  }, 
  showStatus: function(){
    this.$status.text(this.datastore.get("qrcode_status"));
  }, 
  clearQRCodeInput: function(){
    this.$qrcode.val("");
  }, 
  readOnEnter: function(e){
    // if Enter key is typed then call `loadQRCodeInput'
    if(e.keyCode == 13){
      this.loadQRCodeInput();
    } else if(e.ctrlKey && e.keyCode==74){
      this.loadQRCodeInput();
    }
  }, 
  loadQRCodeInput: function(){
    var qrsigned = this.$qrcode.val();
    if((!this.communicating) && this.$el.hasClass("active") ){
      this.communicating = true;
      var self = this;
      var delayTime = 150;
      this._loadQRCodeInput(qrsigned).always(function(){setTimeout(function(){self.communicating = false;}, delayTime)});
    }
  }, 
  _loadQRCodeInput: function(qrsigned){
    var url = this.apiResource["api.ticket.data"];
    var self = this;
    this.datastore.set("qrcode", qrsigned); //todo: using signal.
    return $.getJSON(url, {qrsigned: qrsigned})
      .done(function(data){
        if(data.status == "success"){
          self.messageView.success("QRコードからデータが読み込めました");
          self.datastore.set("qrcode_status", "loaded");
          self.datastore.updateByQRData(data.data);
          self.nextView.drawTicketInfo(data.data);
          return data;
        }

        self.messageView.error(data.message);
        self.datastore.set("qrcode_status", "fail");
        self.datastore.trigger("*refresh");
        return data;
      })
      .fail(function(s, err){
        self.messageView.error(s.responseText);
        self.datastore.set("qrcode_status", "fail");
        self.datastore.trigger("*refresh");
      }).promise();;
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
    if(this.datastore.get("ordered_product_item_token_id") == null){
      this.messageView.alert("QRコードが読み込まれてません")
      return false;
    }
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
    if(!!this.datastore.get("printed")){
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
    this.router = opts.router;
    this.apiResource = opts.apiResource;
    this.datastore.bind("*qr.not.printed", this.createTicket, this);
    // this.datastore.bind("change:ordered_product_item_token_id", this.fetchPinterCandidates, this); //eliminate call times:
    // this.datastore.bind("change:ordered_product_item_token_id", this.fetchTemplateCandidates, this); //eliminate call times:
    // this.datastore.bind("change:ordered_product_item_token_id", this.fetchPageFormatCandidates, this); //eliminate call times:

    this.datastore.bind("change:printer_name", this.setPrinter, this);
    this.datastore.bind("change:ticket_template_id", this.setTicketTemplate, this);
    this.datastore.bind("change:page_format_id", this.setPageFormat, this);

    this.datastore.bind("change:printed", this.sendPrintSignalIfNeed, this);
  }, 
  start: function(){
    this.fetchPinterCandidates();
    this.fetchTemplateCandidates();
    this.fetchPageFormatCandidates();
  }, 
  sendPrintSignalIfNeed: function(){
    if(this.datastore.get("printed") && this.datastore.get("qrcode_status") != "printed" && (!this.datastore.get("canceled"))){
      try {
        this.service.printAll();
        this._updateTicketPrintedAt();
      } catch (e) {
        this.appviews.messageView.error(e);
      }
    }
  }, 
  _updateTicketPrintedAt: function(){
    var params = {
      ordered_product_item_token_id: this.datastore.get("ordered_product_item_token_id"), 
      order_no: this.datastore.get("orderno"), 
      seat_id: this.datastore.get("seat_id"), 
      order_id: this.datastore.get("order_id"), 
      ordered_product_item_token_id: this.datastore.get("ordered_product_item_token_id"), 
      ordered_product_item_id: this.datastore.get("ordered_product_item_id"), 
      ticket_id: this.datastore.get("ticket_template_id")
    };
    var self = this;
    return $.ajax({
      type: "POST", 
      processData: false, 
      data: JSON.stringify(params), 
      contentType: 'application/json',
      dataType: 'json',
      url: this.apiResource["api.ticket.after_printed"]
    }).done(function(data){
      if (data['status'] != 'success') {
        self.appviews.messageView.error(data['message']);
        return;
      }
      self.appviews.messageView.success("チケット印刷できました。");
      self.router.navigate("one", true);
      self.appviews.one.clearQRCodeInput();      
    }).fail(function(s, msg){self.appviews.messageView.error(s.responseText)});
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
        try {
          self.service.addTicket(self.service.createTicketFromJSObject(ticket));
        } catch (e) {
          self.appviews.messageView.error(e);
        }
      });
    }).fail(function(s, msg){self.appviews.messageView.alert(s.responseText)});
  }, 
  fetchPinterCandidates: function(){
    try {
      var printers = this.service.getPrintServices();
      this.appviews.zero.redrawPrinterArea(printers);
    } catch (e) {
      this.appviews.messageView.error(e);
    }
  }, 
  fetchTemplateCandidates: function(){
    try {
      var ticketTemplates = this.service.getTicketTemplates();
      this.appviews.zero.redrawTicketTemplateArea(ticketTemplates);
    } catch (e) {
      this.appviews.messageView.error(e);
    }
  }, 
  fetchPageFormatCandidates: function(){
    try {
      var pageFormats = this.service.getPageFormats();
      this.appviews.zero.redrawPageFormatArea(pageFormats);
    } catch (e) {
      this.appviews.messageView.error(e);
    }
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
    self.navigate("zero", true);
  }
})
