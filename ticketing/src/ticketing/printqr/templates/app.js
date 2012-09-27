// model 
var DataStore = Backbone.Model.extend({
  defaults: {
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
        setTimeout(function(){self.focusNextPage();}, 1)
        return data;})
      .done(this.nextView.updateTicketInfo.bind(this.nextView))
      .fail(function(){
        self.messageView.alert("うまくQRコードを読み込むことができませんでした");
        self.datastore.set("qrcodeStatus", "fail");
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
  updateTicketInfo: function(data){
    this.$orderno.text(data.order);
    this.$codeno.text(data.serial);
    this.$performanceDate.text(data.date);
    this.$performanceName.text(data.performance);
    this.$seatno.text(data.seat_name);
   
    this.datastore.set("orderno", data.order);
    this.datastore.set("performance", data.performance+"("+data.date+")");
    this.datastore.set("product", data.seat_name);
  }
});
var PrinterSelectView = AppPageViewBase.extend({
  initialize: function(opts){
    PrinterSelectView.__super__.initialize.call(this, opts);
  }
});
var PrintConfirmView = AppPageViewBase.extend({
  initialize: function(opts){
    PrintConfirmView.__super__.initialize.call(this, opts);
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
