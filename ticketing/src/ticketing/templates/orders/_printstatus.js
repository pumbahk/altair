var PrintStatusAppView = function(display_field, checkboxes){
  this.display_field = display_field;
  this.checkboxes = checkboxes;
};
PrintStatusAppView.prototype = { //継承しないし
  display_count: function(model){
    var content = "{0} / {1}".replace("{0}", model.count).replace("{1}", model.total_count);
    this.display_field.text(content);
  }, 
  reset_count: function(){
    this.display_count("0 / 0");
  }, 
  cleanup_checkbox: function(){
    this.checkboxes.removeAttr("checked");
  }, 
  check_and_count_checkboxes: function(result){
    var candidates = this.checkboxes;
    var cnt = 0;
    for (var i=0, j=result.length; i<j; i++){
      e = result[i];
      var target = candidates.filter('[name="'+e+'"]')
      if(target.length>0){
        target.attr("checked", "checked");
        cnt += 1;
      }
    };
    return cnt;
  }
};
  
var PrintStatus = function(count, total_count){
  this.count = count; //this page
  this.total_count = total_count;  //total
};
PrintStatus.prototype = {
  "inc": function(){
    this.count += 1;
    this.total_count += 1;
  }, 
  "dec": function(){
    this.count -= 1;
    this.total_count -= 1;
  }, 
  "change": function(d){
    this.count += d;
    this.total_count += d;
  }
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
    $.post(this.resourcs.add, {"target": $e.attr("name")});
    this.model.inc();
    this.view.display_count(this.model);
  }, 
  on_dec: function($e){
    $.post(this.resourcs.remove, {"target": $e.attr("name")});
    this.model.dec();
    this.view.display_count(this.model);
  }, 
  on_addall: function($e){
    var candidates = $("input.printstatus[type='checkbox']:not(:checked)")
    var targets = $.makeArray(candidates.map(function(i, e){return $(e).attr("name")}));
    candidates.attr("checked", "checked");
    if(targets.length > 0){
      console.log(targets.length)
      $.post(this.resourcs.addall, {"targets": targets});
      this.model.change(targets.length);
      this.view.display_count(this.model);
    }
  }, 
  on_removeall: function($e){
    var candidates = $("input.printstatus[type='checkbox']:checked")
    var targets = $.makeArray(candidates.map(function(i, e){return $(e).attr("name")}));
    candidates.removeAttr("checked");
    if(targets.length > 0){
      $.post(this.resourcs.removeall, {"targets": targets});
      this.model.change(-targets.length);
      this.view.display_count(this.model);
    }
  }, 
  on_load: function(){
    var self = this;
    $.getJSON(this.resourcs.load).done(function(data){
      self.view.cleanup_checkbox();     
      var this_page_count = self.view.check_and_count_checkboxes(data.result);
      self.model.total_count = data.count;
      self.model.count = this_page_count;
      self.view.display_count(self.model);
    });
  }, 
  on_reset: function(){
    // this page only or all
    var self = this;
    $.post(this.resourcs.reset).done(function(data){
      self.model.total_count = data.count;
      self.model.count = 0;
      self.view.cleanup_checkbox();
      self.view.display_count(self.model);
    });
  }
};

$.event.add(window, "load", function(){
  var model = new PrintStatus(0);
  var view = new PrintStatusAppView($("#printstatus_count"), $("input.printstatus"));
  var urls = {
    load: "${request.route_url('orders.api.printstatus', action='load')}", 
    add: "${request.route_url('orders.api.printstatus', action='add')}", 
    addall: "${request.route_url('orders.api.printstatus', action='addall')}", 
    remove: "${request.route_url('orders.api.printstatus', action='remove')}", 
    removeall: "${request.route_url('orders.api.printstatus', action='removeall')}", 
    reset: "${request.route_url('orders.api.printstatus', action='reset')}"
  }
  var presenter = new PrintStatusPresenter(model, view, urls);
  $("input.printstatus[type='checkbox']").on("change", presenter.on_check.bind(presenter));
  $("#printstatus_reset").click(presenter.on_reset.bind(presenter));
  $("#addall").click(presenter.on_addall.bind(presenter));
  $("#removeall").click(presenter.on_removeall.bind(presenter));
  presenter.on_load();
});