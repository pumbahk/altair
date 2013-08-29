// buffer
var TicketBuffer = function(){
  return {
    buffers: {}, 
    addTicket: function(ticket){
      var k = ticket.ticket_template_id;
      if(!this.buffers[k]){
        this.buffers[k] = [];
      }
      // console.log("add:"+ticket);
      this.buffers[k].push(ticket);
    }, 
    removeTicket: function(ticket){
    var k = ticket.ticket_template_id;
    var arr = this.buffers[k];
    _(arr).each(function(t, i){
      if(t==ticket){
        // console.log("remove:"+ticket);
        arr[i] = null;
      }
    });
    }, 
    consumeAll: function(fn){
      _(this.buffers).each(function(buf){
      if(!!buf){
        var buf = _.compact(buf);
        var ticket = buf[0];
        fn(buf, ticket.ticket_template_id, ticket.ticket_template_name);
      }
    });
      this.clean();
    }, 
    clean: function(){
      this.buffers = {};
    }
  };
};

// model
var DataStore = Backbone.Model.extend({
  defaults: {
    ticket_buffers: TicketBuffer(), 
    qrcode_status: "preload", 
    auto_trigger: true, 
    qrcode: null,    
    canceled: false, 
    confirmed: false, 
    ordered_product_item_token_id:  null, 
    ordered_product_item_id:  null, 
    printed: false, 
    printed_at: null, 
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
  confirm: function(){
    this.set("printed", false);
    this.set("confirmed", this.get("ordered_product_item_token_id"));
  }, 
  refreshAfterPrint: function(printed){
    this.set("ordered_product_item_token_id", null);
    this.set("printed", printed);
    this.set("qrcode_status", "printed");
    this.set("print_num", 0);
    this.set("qrcode", "");
  }, 
  setPrintStrategy: function(print_unit){
    this.set("print_unit", print_unit);
    switch(print_unit){
    case "order":
        this.set("print_strategy", "(手動)同一注文の券面まとめて発券");
        break;
    case "token":
        this.set("print_strategy", "個別に発券");
        break;
    case "order_auto":
        this.set("print_strategy", "(自動)同一注文の券面まとめて発券");
    }
  }, 
  cleanBuffer: function(){
      this.get("ticket_buffers").clean();
      this.set("print_num", 0);
  }, 
  updateByQRData: function(data){
    // this order is important for call api.applet.ticket.data(ordered_product_item_token_id, printed)

    // initialize
    this.set("printed", false);
    this.set("canceled", false);

    var printed = !!(data.printed) || (!!data.refreshed_at && this.get("confirmed") != data.ordered_product_item_token_id);
    // console.log(JSON.stringify({data: {"printed": data.printed, token_id: data.ordered_product_item_token_id, refreshed_at: data.refreshed_at}, 
    //                             prev: {"printed": this.get("printed"), token_id: this.get("ordered_product_item_token_id"),  confirmed: this.get("confirmed")}, 
    //                             printed: printed}));

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
    this.set("printed_at",  data.printed_at);
    if(printed){
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
    "change #unit_strategy": "checkPrintUnitIsOrder", 
    "keydown input[name='qrcode']": "readOnEnter"
  }, 
  initialize: function(opts){
    QRInputView.__super__.initialize.call(this, opts);
    this.$qrcode = this.$el.find('input[name="qrcode"]');
    this.$status = this.$el.find('#status');
    this.$print_unit_strategy = this.$el.find("#unit_strategy");

    this.datastore.bind("change:qrcode_status", this.showStatus, this);
    this.datastore.bind("*qr.canceled.ticket", this.notifyMessageForCanceled, this);
    this.datastore.bind("*qr.printed.already", this.notifyMessageForPrintedAlready, this);
    this.datastore.bind("*qr.not.printed", this.focusNextPage, this);

    this.communicating = false;
  }, 
  checkPrintUnitIsOrder: function(){
      //console.log(this.$print_unit_strategy.find("option:selected").val());
      this.datastore.setPrintStrategy(this.$print_unit_strategy.find("option:selected").val());
  }, 
  notifyMessageForPrintedAlready: function(){
    this.datastore.set("qrcode", "<confirm>");
    if(getHandleObject(this.datastore).enableForcePrinting()){
      var fmt = 'そのチケットは既に印刷されてます(前回印刷日時:{0}) -- 強制発券しますか？<a id="{1}" class="btn">強制発券する</a>';
      this.messageView.refreshCallback = this.refreshPrintedStatus.bind(this);
      this.messageView.alert(fmt.replace("{0}", this.datastore.get("printed_at"))
                             .replace("{1}", "printed_at_force_refresh") //see: messagView.events
                             ,  true);
    } else{
      var fmt = 'そのチケットは既に印刷されています(前回印刷日時:{0}) -- 自動発券モードでは印刷できません';
      this.messageView.alert(fmt.replace("{0}", this.datastore.get("printed_at")));
    }
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
        self.datastore.confirm();
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
    this.datastore.set("qrcode", "<confirm>");
    if(getHandleObject(this.datastore).enableForcePrinting()){
      var fmt = 'そのチケットはキャンセルされています(キャンセルされた日付:{0}) -- 強制発券しますか？<a id="{1}" class="btn">強制発券する</a>';
      this.messageView.canceledCallback = this.refreshCanceled.bind(this);
      this.messageView.alert(fmt.replace("{0}", this.datastore.get("canceled"))
                             .replace("{1}", "canceled_force_print") //see: messagView.events
                             ,  true);
    } else {
      var fmt = 'そのチケットはキャンセルされています(キャンセルされた日付:{0}) -- 自動発券モードでは印刷できません';
      this.messageView.alert(fmt.replace("{0}", this.datastore.get("canceled")));
    }
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
    this.datastore.cleanBuffer();
    this.datastore.trigger("*refresh");
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
  _isAlreadyQueued: function(qrsigned){
      return this.datastore.get("qrcode") == qrsigned && !(this.datastore.get("canceled"))
  }, 
  loadQRCodeInput: function(){
    var qrsigned = this.$qrcode.val();
    if(this._isAlreadyQueued(qrsigned)){
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
    if(!this._isAlreadyQueued(qrsigned)){
        this.datastore.cleanBuffer();
    }
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
 _drawTicketInfoTable: function(data){
    //console.dir(data);
    this.$user.text(data.user);
    this.$codeno.text(data.codeno);
    this.$orderno.text(data.orderno);
    this.$performanceDate.text(data.performance_date);
    this.$performanceName.text(data.performance_name);
    this.$product_name.text(data.product_name);
    this.$seatno.text(data.seat_name);  
  }, 
  _drawTicketInfoNote: function(data){
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
  }, 
  drawTicketInfo: function(data){
    this._drawTicketInfoTable(data);
    this._drawTicketInfoNote(data);
  }
});

var FormatChoiceView = AppPageViewBase.extend({
  events:{
    "change #printer input": "printerSettingsChanged", 
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
    // まとめて注文する際には、printボタン押下後bufferから消費されてticket_template_idが埋められる
    // if(this.datastore.get("ticket_template_id") == null){
    //   this.messageView.alert("チケットテンプレートが設定されていません")
    //   this.router.navigate("zero", true);
    //   return false;
    // }
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

var PrintableTicketsSelectView = Backbone.View.extend({
  events: {
    'change #printable_tickets_box input[type="checkbox"]': "onToggleCheckBox"
  }, 
  initialize: function(opts){
    this.datastore = opts.datastore;
    this.ticketBuffer = opts.datastore.get("ticket_buffers");
    this.callback = opts.callback;
    this.$checkboxArea = this.$el.find("#printable_tickets_box");
    this.tickets = [];
  },
  toggleCheckBox: function($e){
    if($e.attr("checked") == "checked"){
      this.ticketBuffer.addTicket(this.tickets[$e.attr("name")]);
      this.datastore.set("print_num",  this.datastore.get("print_num") + 1);
    } else {
      this.ticketBuffer.removeTicket(this.tickets[$e.attr("name")]);
      this.datastore.set("print_num",  this.datastore.get("print_num") - 1);
    }
  }, 
  onToggleCheckBox: function(e){
    var $e = $(e.currentTarget);
    this.toggleCheckBox($e);
  }, 
  show: function(){
    this.$el.show();
  }, 
  hide: function(){
    this.$el.hide();
  }, 
  draw: function(tickets){
    this.tickets = tickets;
    var root = this.$checkboxArea
    root.empty();
    var self = this;
    var target_id = this.datastore.get("ordered_product_item_token_id");
    _(this.tickets).each(function(t, i){
      var $e = self._createRow(t, i, target_id);
      root.append($e);
    });
    this.show();
  }, 
  _createRowCheckbox: function(t, i, decorate_fn, checked){
    // <td><input type="checkbox" name="0"  checked="checked"></input></td><td>コートエンド北(1階 コートエンド北 1列 42番)</td>
    var tr = $('<tr>');
    var checkbox = $('<input type="checkbox">').attr('name', i).attr("id", t.ordered_product_item_token_id);
    if(checked){
      checkbox.attr('checked', 'checked');
    }
    tr.append($('<td>').append(checkbox));
    tr.append($('<td>').text(t.codeno));
    tr.append(decorate_fn($('<td>').text(t.ticket_name), t));
    return tr
  }, 
  _withPrintedMessage: function($td, t){
    return $td.append($('<span class="label">').text(t.refreshed_at ? ("印刷済み:"+t.printed_at+"(再印刷許可:)"+t.refreshed_at) : ("印刷済み"+t.printed_at)));
  }, 
  _createRow: function(t, i, target_id){
    var is_inputed_ticket = t.ordered_product_item_token_id == target_id;
    if(t.printed_at && ! is_inputed_ticket){  //printed
      return this._createRowCheckbox(t, i, this._withPrintedMessage);
    } else{
      this.ticketBuffer.addTicket(t);
      this.datastore.set("print_num",  this.datastore.get("print_num") + 1);
      if(t.printed_at && is_inputed_ticket){
          return this._createRowCheckbox(t, i, this._withPrintedMessage,  true);
      }else {
          return this._createRowCheckbox(t, i, function(e){return e;}, true);
      }
    }
  }
})

//HnadleObject..
var actions = {
  enableForcePrinting: null, 
  createTicket: null, 
  addTicket: null, 
  printAll: null, 
  updatePrintedAt: null
};

var PrintUnitIsToken = {
  enableForcePrinting: function(){
    return true;
  }, 
  createTicket: function createTicket(appletView){
    return appletView.createTicketUnitByToken().done(appletView.autoPrint.bind(appletView));
  }, 
  addTicket: function addTicket(datastore, service, ticket){
    service.addTicket(service.createTicketFromJSObject(ticket));
    datastore.set("print_num",  datastore.get("print_num") + 1);
  }, 
  printAll: function printAll(appletView){
    appletView.service.printAll();
  }, 
  getAfterPrintApi: function getAfterPrintApi(apiResource){
    return apiResource["api.ticket.after_printed"];      
  }
};
var PrintUnitIsOrder = {
  enableForcePrinting: function(){
    return true;
  }, 
  createTicket: function createTicket(appletView){
    return appletView.createTicketUnitByOrder();
  }, 
  addTicket: function addTicket(datastore, service, ticket){
    datastore.get("ticket_buffers").addTicket(ticket);        
    datastore.set("print_num",  datastore.get("print_num") + 1);
  }, 
  printAll: function printAll(appletView){
    appletView._printAllWithBuffer();
  }, 
  getAfterPrintApi: function getAfterPrintApi(apiResource){
    return apiResource["api.ticket.after_printed_order"];      
  }
};
var PrintUnitIsOrderAutoPrint ={
  enableForcePrinting: function(){
    return false;
  }, 
  createTicket: function createTicket(appletView){
    return appletView.createTicketUnitByOrder().done(appletView.autoPrint.bind(appletView));
  }, 
  addTicket: function addTicket(datastore, service, ticket){
    datastore.get("ticket_buffers").addTicket(ticket);        
    datastore.set("print_num",  datastore.get("print_num") + 1);
  }, 
  printAll: function printAll(appletView){
    appletView._printAllWithBuffer();
  }, 
  getAfterPrintApi: function getAfterPrintApi(apiResource){
    return apiResource["api.ticket.after_printed_order"];      
  }
};

var HandleTable = {
  token: PrintUnitIsToken, 
  order: PrintUnitIsOrder, 
  order_auto: PrintUnitIsOrderAutoPrint
};

var getHandleObject = function(model){
  // console.log(model.get("print_unit"));
  return HandleTable[model.get("print_unit")];
}

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

    this.consumed_tokens = [];
  }, 
  start: function(){
    this.fetchPinterCandidates();
    this.fetchPageFormatCandidates();
  }, 
  _addTicket: function(ticket){
    try {
        getHandleObject(this.datastore).addTicket(this.datastore, this.service, ticket);
    } catch (e) {
      this.appviews.messageView.error(e);
    }
  }, 
  _afterPrintAll: function(){
    var self = this;
    this._updateTicketPrintedAt()
      .done(function(data){
        if (data['status'] != 'success') {
          self.appviews.messageView.error(data['message']);
          self.datastore.set("printed", false);
          return;
        }
        self.datastore.refreshAfterPrint(data.printed);
        self.appviews.messageView.success("チケット印刷できました。");
        self.router.navigate("one", true);
        self.appviews.one.clearQRCodeInput();      
      }).fail(function(s, msg){
        self.datastore.set("printed", false);
        self.appviews.messageView.error(s.responseText)
      })
      .always(function(){
        self.datastore.set("confirmed", false);
        self.trigger("*event.qr.printed");
      });
  }, 
  _printAllWithBuffer: function(){
    var self = this;
    this.datastore.get("ticket_buffers").consumeAll(function(buf, template_id, template_name){
      self.datastore.set("ticket_template_id", template_id);
      self.datastore.set("ticket_template_name", template_name);
      //変更内容伝搬されるまで時間がかかる？信じるよ？
      _(buf).each(function(ticket){
        self.service.addTicket(self.service.createTicketFromJSObject(ticket));
        self.consumed_tokens.push(ticket.ordered_product_item_token_id);
      });
      self.service.printAll();
    });
  }, 
  sendPrintSignalIfNeed: function(){
    if(this.datastore.get("printed")){
      try {
        this.appviews.messageView.info("チケット印刷中です.....");
        getHandleObject(this.datastore).printAll(this);
        this._afterPrintAll();
      } catch (e) {
        this.datastore.set("printed", false);
        this.appviews.messageView.error(e);
      }
    }
  }, 
  _updateTicketPrintedAt: function(callback){
    var apiUrl = getHandleObject(this.datastore).getAfterPrintApi(this.apiResource);
    var params = {
      ordered_product_item_token_id: this.datastore.get("ordered_product_item_token_id"), 
      order_no: this.datastore.get("orderno"), 
      seat_id: this.datastore.get("seat_id"), 
      order_id: this.datastore.get("order_id"), 
      ordered_product_item_token_id: this.datastore.get("ordered_product_item_token_id"), 
      ordered_product_item_id: this.datastore.get("ordered_product_item_id"), 
      ticket_id: this.datastore.get("ticket_template_id"), 
      consumed_tokens: this.consumed_tokens
    };
    var self = this;
    return $.ajax({
      type: "POST", 
      processData: false, 
      data: JSON.stringify(params), 
      contentType: 'application/json',
      dataType: 'json',
      url: apiUrl
    }).done(function(data){self.consumed_tokens = []; return data;}).promise();
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
      getHandleObject(this.datastore).createTicket(this);
  }, 
  createTicketUnitByOrder: function(){
    var orderno = this.datastore.get("orderno");
    var self = this;
    return $.ajax({
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
      // 印刷するticketの情報を管理する
      self.appviews.selectTicketView.draw(data["data"]);

      var fmt = "まとめて注文した際には自動的に印刷しません。印刷するには、購入情報を確認した後、印刷ボタンを押してください<br/>";
      fmt = fmt + "(既に印刷された券面については印刷されません。)<br/";
      self.router.navigate("two", true); //確認画面へfocus
      self.appviews.messageView.info(fmt, true);
    }).fail(function(s, msg){self.appviews.messageView.error(s.responseText)});
  }, 
  createTicketUnitByToken: function(){
    var tokenId = this.datastore.get("ordered_product_item_token_id");
    var self = this;
    return $.ajax({
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
      // まとめて券面選択するelementを隠す
      self.appviews.selectTicketView.hide();

      self.appviews.messageView.success("券面データが保存されました");
      _.each(data['data'], function (ticket) {
        if(!!(ticket.ticket_template_id)){
            self.datastore.set("ticket_template_id", ticket.ticket_template_id);
            self.datastore.set("ticket_template_name", ticket.ticket_template_name);
        }
        //alert(self.datastore.get("ordered_product_item_token_id"));
        self.appviews.messageView.info("券面印刷用データを追加中です...");
        self._addTicket(ticket);
      });
    }).fail(function(s, msg){self.appviews.messageView.error(s.responseText)});
  }, 
  autoPrint: function(){
    if(this.datastore.get("auto_trigger")){
      this.datastore.trigger("*qr.validate.preprint");
    }else{
      var fmt = "キャンセル済みのチケットあるいはチケットは自動的に印刷しません。印刷するには、購入情報を確認した後、印刷ボタンを押してください";
      this.appviews.messageView.alert(fmt);
    }
  }, 
  fetchPinterCandidates: function(){
    try {
      var printers = this.service.getPrintServices();
      this.appviews.zero.redrawPrinterArea(printers);
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
