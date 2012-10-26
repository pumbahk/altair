// model
var DataStore = Backbone.Model.extend({
  defaults: {
    qrcode_status: "preload", 
    auto_trigger: true, 
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

    print_unit: "token", //token or order
    print_strategy: "個別に発券", 
    print_num: 0
  }, 
  setPrintStrategy: function(print_unit){
    if(print_unit=="order"){
      this.set("print_unit", "order");
      this.set("print_strategy", "同一注文の券面まとめて発券");
    }else {
      this.set("print_unit", "token");
      this.set("print_strategy", "個別に発券");
    }
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
      this.set("qrcode_status", "printed");
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
    // this.model.bind("change", function(){console.info(JSON.stringify(this.model.toJSON()))}, this);
    this.model.bind("change:print_strategy", this.showPageStrategy, this);
    this.model.bind("change:print_num", this.showPageNum, this);
    this.model.bind("change:qrcode_status", this.showQrcodeStatus, this);
    this.model.bind("change:orderno", this.showOrderno, this);
    this.model.bind("change:performance", this.showPerformance, this);
    this.model.bind("change:product", this.showProduct, this);
    this.model.bind("change:printer_name", this.showPrinter, this);
    this.model.bind("change:page_format_name", this.showPageFormat, this);
    this.model.bind("change:ticket_template_name", this.showTicketTemplate, this);
    this.model.bind("*refresh", this.refresh, this);

    this.$print_strategy = this.$el.find("#desc_print_strategy");
    this.$print_num = this.$el.find("#desc_print_num");
    this.$qrcode_status = this.$el.find("#desc_qrcode_status");
    this.$orderno = this.$el.find("#desc_orderno");
    this.$performance = this.$el.find("#desc_performance");
    this.$product = this.$el.find("#desc_product");
    this.$printer = this.$el.find("#desc_printer");
    this.$ticket_template = this.$el.find("#desc_ticket_template");
    this.$page_format = this.$el.find("#desc_page_format");

    this.$qr_printed_shortcut = this.$el.find("#desc_qr_printed_shortcut");
    this.$qr_unprinted_shortcut = this.$el.find("#desc_qr_unprinted_shortcut");
  }, 
  showPageStrategy: function(){
    this.$print_strategy.text(this.model.get("print_strategy"));
  }, 
  showPageNum: function(){
    this.$print_num.text(this.model.get("print_num"));
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
  }, 
  onCurrenttimeChanged: function(data){
    this.$qr_printed_shortcut.text(data.qr_printed);
    this.$qr_unprinted_shortcut.text(data.qr_unprinted);
  }
});


var MessageView = message({}).MessageInformationView.extend({
  events: {
    "click #printed_at_force_refresh": "sendRefreshPrintedStatusSignal", 
    "click #canceled_force_print": "sendCanceledForcePrintSignal"
  }, 
  sendRefreshPrintedStatusSignal: function(){
    if(!!(this.refreshCallback && window.confirm("本当に強制再発券しますか？"))){
      this.refreshCallback();
      this.refreshCallback = false;
    }
  }, 
  sendCanceledForcePrintSignal: function(){
    if(!!(this.canceledCallback && window.confirm("本当にキャンセル済みのチケットを発券しますか？"))){
      this.canceledCallback();
      this.canceledCallback = false;
    }
  }, 
  initialize: function(opts){
    MessageView.__super__.initialize.call(this, opts);
    this.refreshCallback = false;
    this.canceledCallback = false;
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
    "click input[name='print_unit_is_order']": "checkPrintUnitIsOrder", 
    "keydown input[name='qrcode']": "readOnEnter"
  }, 
  initialize: function(opts){
    QRInputView.__super__.initialize.call(this, opts);
    this.$qrcode = this.$el.find('input[name="qrcode"]');
    this.$status = this.$el.find('#status');
    this.$print_unit_is_order = this.$el.find("input[name='print_unit_is_order']");

    this.datastore.bind("change:qrcode_status", this.showStatus, this);
    this.datastore.bind("*qr.canceled.ticket", this.notifyMessageForCanceled, this);
    this.datastore.bind("*qr.printed.already", this.notifyMessageForPrintedAlready, this);
    this.datastore.bind("*qr.not.printed", this.focusNextPage, this);

    this.communicating = false;
  }, 
  checkPrintUnitIsOrder: function(){
    if(this.$print_unit_is_order.attr("checked") == "checked"){
      this.datastore.setPrintStrategy("order");
    }else {
      this.datastore.setPrintStrategy("token");
    }
  }, 
  notifyMessageForPrintedAlready: function(){
    var fmt = 'そのチケットは既に印刷されてます(前回印刷日時:{0}) -- 強制発券しますか？<a id="{1}" class="btn">強制発券する</a>';
    this.datastore.set("qrcode", "<confirm>");
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

      self._loadQRCodeInput(self.$qrcode.val(), false);
    }).fail(function(s, msg){self.messageView.error(s.responseText)});
  }, 
  notifyMessageForCanceled: function(){
    var fmt = 'そのチケットはキャンセルされています(キャンセルされた日付:{0}) -- 強制発券しますか？<a id="{1}" class="btn">強制発券する</a>';
    this.datastore.set("qrcode", "<confirm>");
    this.messageView.canceledCallback = this.refreshCanceled.bind(this);
    this.messageView.alert(fmt.replace("{0}", this.datastore.get("canceled"))
                              .replace("{1}", "canceled_force_print") //see: messagView.events
                            ,  true);
  }, 
  refreshCanceled: function(){
    this.datastore.set("canceled", false);
    this.datastore.set("qrcode_status", "canceld(but force print)")
    this.messageView.success("キャンセルされたチケットを印刷できるようにしました。")

    // log
    var message = "*qrlog* canceled ticket force print order={0} token={1}"
      .replace("{0}", this.datastore.get("order_id"))
      .replace("{1}", this.datastore.get("ordered_product_item_token_id"))
    $.post(this.apiResource["api.log"], {"log": message})

    this.datastore.set("auto_trigger", false);
    this.datastore.trigger("*qr.not.printed");
  }, 
  showStatus: function(){
    this.$status.text(this.datastore.get("qrcode_status"));
  }, 
  clearQRCodeInput: function(){
    this.$qrcode.val("");
  }, 
  readOnEnter: function(e){
    // if Enter key is typed then call `loadQRCodeInput'
    if (e.keyCode == 13 || (e.ctrlKey && e.keyCode == 74 /* CTRL-J */)) {
      this.loadQRCodeInput();
    } else if ((e.ctrlKey || e.metaKey) && e.keyCode == 86) {
      // CTRL-V or META-V
      return true;
    } else if (e.keyCode == 8) {
      this.$qrcode[0].value = '';
    } else {
      this.$qrcode[0].value += String.fromCharCode(KeycodeMapping.translate(e.shiftKey, e.keyCode));
    }
    return false;
  }, 
  loadQRCodeInput: function(){
    var qrsigned = this.$qrcode.val();
    if(this.datastore.get("qrcode") == qrsigned && !(this.datastore.get("canceled"))){
      this.messageView.alert("既に印刷キューに入っています。")
      return ;
    }
    if((!this.communicating) && this.$el.hasClass("active") ){
      this.communicating = true;
      var self = this;
      var delayTime = 150;
      this._loadQRCodeInput(qrsigned, true).always(function(){setTimeout(function(){self.communicating = false;}, delayTime)});
    }
  }, 
  _loadQRCodeInput: function(qrsigned,  auto_trigger){
    var url = this.apiResource["api.ticket.data"];
    var self = this;
    this.datastore.set("qrcode", qrsigned); //todo: using signal.
    this.datastore.set("auto_trigger",  auto_trigger);

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
      })
      .always(function(){self.trigger("*event.qr.loaded");})
      .promise();
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
    this.$note = this.$el.find("#note");
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
    var $note = this.$note;
    $note.empty();
    if (data.note) {
      $note.parent().show();
      var first = true;
      jQuery.each((data.note + "").split(/\s*\n\s*/), function (_, line) {
        if (!first)
          $note[0].appendChild(document.createElement("br"));
        $note[0].appendChild(document.createTextNode(line));
        first = false;
      });
    } else {
      this.$note.parent().hide();
    }
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
    this.datastore.bind("*qr.validate.preprint", this.clickPrintButton, this);
  }, 
  _validationPrePrint: function(){
    if(this.datastore.get("ordered_product_item_token_id") == null){
      this.messageView.alert("QRコードが読み込まれてません")
      this.router.navigate("one", true);
      return false;
    }
    if(this.datastore.get("ticket_template_id") == null){
      this.messageView.alert("チケットテンプレートが設定されていません")
      this.router.navigate("zero", true);
      return false;
    }
    if(this.datastore.get("page_format_id") == null){
      this.messageView.alert("ページフォーマットが設定されていません");
      this.router.navigate("zero", true);
      return false;
    }
    if(this.datastore.get("printer_name") == null){
      this.messageView.alert("プリンタが設定されていません");
      this.router.navigate("zero", true);
      return false;
    }
    return true;
  }, 
  clickPrintButton: function(){
    this.messageView.info("チケット印刷中です...");
    if(!this._validationPrePrint()){
      return;
    }
    if(!!this.datastore.get("printed")){
      this.messageView.alert("既に印刷済みです。");
    }else{
      this.datastore.set("printed", true);
      this.datastore.trigger("*qr.print.signal");
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

    this.datastore.bind("change:printer_name", this.setPrinter, this);
    this.datastore.bind("change:ticket_template_id", this.setTicketTemplate, this);
    this.datastore.bind("change:page_format_id", this.setPageFormat, this);

    this.datastore.bind("*qr.print.signal", this.sendPrintSignalIfNeed, this);
  }, 
  start: function(){
    this.fetchPinterCandidates();
    this.fetchTemplateCandidates();
    this.fetchPageFormatCandidates();
  }, 
  _addTicket: function(ticket){
    try {
      this.service.addTicket(this.service.createTicketFromJSObject(ticket));
      this.datastore.set("print_num",  this.datastore.get("print_num") + 1);
    } catch (e) {
      this.appviews.messageView.error(e);
    }
  }, 
  _printAll: function(){
    var self = this;
    this.appviews.messageView.info("チケット印刷中です.....");
    this.service.printAll();
    this._updateTicketPrintedAt()
      .done(function(data){
        if (data['status'] != 'success') {
          self.appviews.messageView.error(data['message']);
          self.datastore.set("printed", false);
          return;
        }
        self.datastore.set("qrcode_status", "printed");
        self.datastore.set("printed", data.printed);
        self.datastore.set("print_num", 0);
        self.datastore.set("qrcode", "");
        self.appviews.messageView.success("チケット印刷できました。");
        self.router.navigate("one", true);
        self.appviews.one.clearQRCodeInput();      
      }).fail(function(s, msg){
        self.datastore.set("printed", false);
        self.appviews.messageView.error(s.responseText)
      })
      .always(function(){
        self.trigger("*event.qr.printed");
      });
  }, 
  sendPrintSignalIfNeed: function(){
    if(this.datastore.get("printed")){
      try {
        //alert("print!!");
        this._printAll();
      } catch (e) {
        this.datastore.set("printed", false);
        this.appviews.messageView.error(e);
      }
    }
  }, 
  _updateTicketPrintedAt: function(callback){
    if(this.datastore.get("print_unit") == "order"){
      var apiUrl = this.apiResource["api.ticket.after_printed_order"]      
    }else {
      var apiUrl = this.apiResource["api.ticket.after_printed"]      
    }

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
      url: apiUrl
    }).promise();
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
    var print_unit = this.datastore.get("print_unit");
    if(print_unit == "order"){
      return this.createTicketUnitByOrder()
    }else {
      return this.createTicketUnitByToken()
    }
  }, 
  createTicketUnitByOrder: function(){
    var orderno = this.datastore.get("orderno");
    var self = this;
    $.ajax({
      type: 'POST',
      processData: false,
      data: JSON.stringify({ order_no: orderno }),
      contentType: 'application/json',
      dataType: 'json',
      url: this.apiResource["api.ticketdata_from_order_no"]
    }).done(function (data) {
      if (data['status'] != 'success') {
        self.appviews.messageView.error(data['message']);
        return;
      }
      self.appviews.messageView.success("券面データが保存されました");
      var printing_tickets = []
      self.appviews.messageView.info("券面印刷用データを追加中です...");
      $.each(data['data'], function (_, ticket) {
        //alert(self.datastore.get("ordered_product_item_token_id"));
        if(!ticket.printed_at){
          printing_tickets.push(ticket.ticket_name);
          self._addTicket(ticket);
        }else {
          printing_tickets.push(ticket.ticket_name + "--(印刷済み:{0})".replace("{0}", ticket.printed_at));
        }
      });
      var fmt = "まとめて注文した際には自動的に印刷しません。印刷するには、購入情報を確認した後、印刷ボタンを押してください<br/>";
      fmt = fmt + "(既に印刷された券面については印刷されません。)<br/";
      fmt = fmt + "<ul><li>" + printing_tickets.join("</li>\n<li>") + "</li></ul>";
      self.appviews.messageView.info(fmt, true);
    }).fail(function(s, msg){self.appviews.messageView.error(s.responseText)});
  }, 
  createTicketUnitByToken: function(){
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
        self.appviews.messageView.error(data['message']);
        return;
      }
      self.appviews.messageView.success("券面データが保存されました");
      $.each(data['data'], function (_, ticket) {
        //alert(self.datastore.get("ordered_product_item_token_id"));
        self.appviews.messageView.info("券面印刷用データを追加中です...");
        self._addTicket(ticket);
      });
      if(self.datastore.get("auto_trigger")){
        self.datastore.trigger("*qr.validate.preprint");
      }else{
        var fmt = "キャンセル済みのチケットあるいはチケットは自動的に印刷しません。印刷するには、購入情報を確認した後、印刷ボタンを押してください";
        self.appviews.messageView.alert(fmt);
      }
    }).fail(function(s, msg){self.appviews.messageView.error(s.responseText)});
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
