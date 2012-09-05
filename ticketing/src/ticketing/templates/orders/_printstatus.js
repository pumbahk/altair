var PrintStatusAppView = function(display_field, checkboxes){
  this.display_field = display_field;
  this.checkboxes = checkboxes;
};
PrintStatusAppView.prototype = { //継承しないし
  display_count: function(n){
    this.display_field.text(n);
  }, 
  reset_count: function(){
    this.display_count("0");
  }, 
  cleanup_checkbox: function(){
    this.checkboxes.removeAttr("checked");
  }
};
  
var PrintStatus = function(count){
  this.count = count;
};
PrintStatus.prototype = {
  "inc": function(){this.count += 1;}, 
  "dec": function(){this.count -= 1;}
}

var PrintStatusPresenter = function(model, view, resourcs){
  this.model = model;
  this.view = view;
  this.resourcs = resourcs;
};

PrintStatusPresenter.prototype = {
  on_check: function(e){
    var $e = $(e.currentTarget);
    if(!!$e.attr("checked")){
      this.on_inc($e);
    } else {
      this.on_dec($e);
    }
  }, 
  on_inc: function($e){
    this.model.inc();
    this.view.display_count(this.model.count);
  }, 
  on_dec: function($e){
    this.model.dec();
    this.view.display_count(this.model.count);
  }, 
  on_load: function(){
    var self = this;
    $.getJSON(this.resourcs.load).done(function(data){
      self.view.cleanup_checkbox();
      self.model.count = data.count;
      self.view.display_count(self.model.count);
    });
  }
};

$(function(){
  var model = new PrintStatus(0);
  var view = new PrintStatusAppView($("#printstatus_count"), $("input.printstatus"));
  var urls = {
    load: "${request.route_url('orders.api.printstatus', action='load')}"
  }
  var presenter = new PrintStatusPresenter(model, view, urls);
  $("input.printstatus[type='checkbox']").on("change", presenter.on_check.bind(presenter));
  presenter.on_load();
})