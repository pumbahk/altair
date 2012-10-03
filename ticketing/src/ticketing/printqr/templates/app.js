// model 
var DataStore = Backbone.Model.extend({
  defaults: {
    orderId: null, 

    qrcodeStatus: "preload", 
    qrcode: null, 
    
    orderno: null,
    performance: null,
    product: null,
  }
});

// view
var DataStoreDescriptionView = Backbone.View.extend({
  initialize: function(){
    this.model.bind("change:qrcodeStatus", this.showQrcodeStatus, this);
    this.model.bind("change:orderno", this.showOrderno, this);
    this.model.bind("change:performance", this.showPerformance, this);
    this.model.bind("change:product", this.showProduct, this);
    this.model.bind("refresh", this.refresh, this);

    this.$qrcodeStatus = this.$el.find("#desc_qrcodeStatus");
    this.$orderno = this.$el.find("#desc_orderno");
    this.$performance = this.$el.find("#desc_performance");
    this.$product = this.$el.find("#desc_product");
  }, 
  showQrcodeStatus: function(){
    this.$qrcodeStatus.text(this.model.get("qrcodeStatus"));
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
    "click #load_button": "loadQRSigned"
  }, 
  initialize: function(opts){
    QRInputView.__super__.initialize.call(this, opts);
    this.$qrcode = this.$el.find('input[name="qrcode"]')
    this.$status = this.$el.find('#status')
    this.datastore.bind("change:qrcodeStatus", this.showStatus, this);
  }, 
  showStatus: function(){
    this.$status.text(this.datastore.get("qrcodeStatus"));
  }, 
  loadQRSigned: function(){
    var url = this.apiResource["api.ticket.data"];
    var self = this;
    $.getJSON(url, {qrsigned: this.$qrcode.val()})
      .done(function(data){
        self.messageView.success("QRコードからデータが読み込めました");
        self.datastore.set("qrcodeStatus", "loaded");
        //setTimeout(function(){self.focusNextPage();}, 1)
        return data;})
      .done(this.nextView.updateTicketInfo.bind(this.nextView))
      .fail(function(s, err){
        self.messageView.alert("うまくQRコードを読み込むことができませんでした");
        self.datastore.set("qrcodeStatus", "fail");
        self.datastore.trigger("refresh");
      })
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
  updateTicketInfo: function(data){
    //console.dir(data);
    this.$user.text(data.user);
    this.$codeno.text(data.codeno);
    this.$orderno.text(data.orderno);
    this.$performanceDate.text(data.performance_date);
    this.$performanceName.text(data.performance_name);
    this.$product_name.text(data.product_name);
    this.$seatno.text(data.seat_name);
   
    this.datastore.set("orderId", data.order_id);
    this.datastore.set("orderno", data.orderno);
    this.datastore.set("performance", data.performance_name+" -- "+data.performance_date);
    this.datastore.set("product", data.product_name+"("+data.seat_name+")");
  }
});

var PrinterSelectView = AppPageViewBase.extend({
  initialize: function(opts){
    PrinterSelectView.__super__.initialize.call(this, opts);
    this.$pageFormat = this.$el.find("#page_format");
  }
});

var PrintConfirmView = AppPageViewBase.extend({
  initialize: function(opts){
    PrintConfirmView.__super__.initialize.call(this, opts);
  }
});

var AppletView = Backbone.View.extend({
  initialize: function(opts){
    this.appviews = opts.appviews;
    this.datastore = opts.datastore;
    this.service = opts.service;
    this.createProxy = opts.createProxy;
    
    this.datastore.bind("change:orderId", this.fetchFormats, this);
  }, 
  
  fetchFormats: function(){
    this.service.filterByOrderId(this.datastore.get("orderId"));
    var formats = this.service.getTicketFormats();
    var targetArea = this.appviews.three.$pageFormat;
    targetArea.empty();
    for(var i = formats.iterator(); i.hasNext();){
      var format = i.next();
      var e = $('<div class="control-group">');
      e.append($('<span>').text(format.getName()));
      e.append($('<input type="radio" name="pageformat">').attr("value", format.getId()));
      targetArea.append(e);
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
  }, 
  start: function(){
    var self = this;
    $("a[href^=#]").on("click",  function(e){
      self.navigate($(this).attr("href").substr(1), true);
      e.preventDefault();
    });
    if(location.href.search("#") == -1){
      self.navigate("one", true); //todo: cache
    }
  }
})
