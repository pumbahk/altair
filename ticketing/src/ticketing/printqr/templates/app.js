var QRInputView = Backbone.View.extend({
});
var TicketInfoView = Backbone.View.extend({
});
var PrinterSelectView = Backbone.View.extend({
});
var PrintConfirmView = Backbone.View.extend({
});

var AppRouter = Backbone.Router.extend({
  routes: {
    ":page": "show_page"
  }, 
  show_page:  function(page){
    $(".onepage").hide();
    $(".onepage#{0}".replace("{0}", page)).show();
  }, 
  start: function(){
    var self = this;
    $("a[href^=#]").on("click",  function(e){
      self.navigate($(this).attr("href").substr(1), true);
      e.preventDefault();
    });
    
  }
})

$(function(){
  var app_router = new AppRouter()
  //Backbone.history.start({pushState: true,  root: "/"})
Backbone.history.start({root: "/"})
  app_router.start.call(app_router);
})