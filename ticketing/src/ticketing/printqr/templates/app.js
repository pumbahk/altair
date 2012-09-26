var QRInputView = Backbone.View.extend({
  events: {
    "click #load_button": "load_qrsigned"
  }, 
  initialize: function(opts){
    this.api_resource = opts.api_resource;
    this.$qrcode = this.$el.find('input[name="qrcode"]')
    this.nextview = null;
  }, 
  load_qrsigned: function(){
    var url = this.api_resource["api.ticket.data"];
    $.getJSON(url, {qrsigned: this.$qrcode.val()})
      .done(function(data){return data})
      .done(this.nextview.update_ticket_info.bind(this.nextview));
  } 
});

var TicketInfoView = Backbone.View.extend({
  initialize: function(opts){
    this.api_resource = opts.api_resource;
    this.nextview = null;
    this.$user = this.$el.find("#user");
    this.$codeno = this.$el.find("#codeno");
    this.$orderno = this.$el.find("#orderno");
    this.$performance_name = this.$el.find("#performance_name");
    this.$performance_date = this.$el.find("#performance_date");
    this.$product_name = this.$el.find("#product_name");
    this.$seatno = this.$el.find("#seatno");
  }, 
  update_ticket_info: function(data){
    console.dir(data);
    this.$seatno.text(data.seat_name);
  }
});
var PrinterSelectView = Backbone.View.extend({
  initialize: function(opts){
    this.api_resource = opts.api_resource;
    this.nextview = null;
  }
});
var PrintConfirmView = Backbone.View.extend({
  initialize: function(opts){
    this.api_resource = opts.api_resource;
    this.nextview = null;
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
      self.navigate("#one", true); //todo: cache
    }
  }
})
