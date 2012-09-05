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
  }, 
  collect_save_targets: function(){
    return this.checkboxes.filter(":checked");
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
      
      var candidates = self.view.checkboxes;
      for (var i=0, j=data.result.length; i<j; i++){
        e = data.result[i];
        candidates.filter('[name="'+e+'"]').attr("checked", "checked");
      };
      self.view.display_count(self.model.count);
    });
  }, 
  on_save: function(e){
    var self = this;
    var targets = this.view.collect_save_targets();
    targets = $.makeArray(targets.map(function(i, e){ return $(e).attr("name")}));
    params = {"targets": JSON.stringify(targets)};
    $.post(this.resourcs.save, {"targets": targets});
    return false;
  }
};

$(function(){
  var model = new PrintStatus(0);
  var view = new PrintStatusAppView($("#printstatus_count"), $("input.printstatus"));
  var urls = {
    load: "${request.route_url('orders.api.printstatus', action='load')}", 
    save: "${request.route_url('orders.api.printstatus', action='save')}"
  }
  var presenter = new PrintStatusPresenter(model, view, urls);
  $("input.printstatus[type='checkbox']").on("change", presenter.on_check.bind(presenter));
  $("#printstatus_save").click(presenter.on_save.bind(presenter));
  presenter.on_load();
})