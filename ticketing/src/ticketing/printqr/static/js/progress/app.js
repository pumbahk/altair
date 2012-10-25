// require:backbone.js, ../message.js

// model
// model structure is tree.
var DataStore = Backbone.Model.extend({
  defaults: {
    performance: null, 
    total_result: null, 
    current_time: null
  }, 
  updateFromPerformanceChangeApi: function(data){
    this.get("performance").updateFromPerformanceChangeApi(data.performance);
    this.get("total_result").updateFromPerformanceChangeApi(data.total_result);
    this.set("current_time", data.current_time);
  }
});

var Performance = Backbone.Model.extend({
  defaults: {
    start_on: null, 
    name: "", 
    pk: -1
  }, 
  updateFromPerformanceChangeApi: function(data){
    this.set("start_on", data.start_on);
    this.set("name", data.name);
    this.set("pk", data.pk);
  }
});

var TotalResult = Backbone.Model.extend({
  defaults: {
    total: 0, 

    total_qr: 0, 
    total_other: 0, 

    qr_printed: 0, 
    qr_unprinted: 0
  }, 
  updateFromPerformanceChangeApi: function(data){
    this.set("total", data.total);
    this.set("total_qr", data.total_qr);
    this.set("total_other", data.total_other);
    this.set("qr_printed", data.qr_printed);
    this.set("qr_unprinted", data.qr_unprinted);
    this.trigger("*update.total_result");
  }
});

var ApiService = Backbone.View.extend({
  initialize: function(opts){
    this.apiResource = opts.apiResource;
  }, 
  _postRequest: function(apiUrl, params){
    return $.ajax({
      type: "POST", 
      processData: false, 
      data: JSON.stringify(params), 
      contentType: 'application/json',
      dataType: 'json',
      url: apiUrl
    })
  }, 
  getPerformanceData: function(performance_id){
    var url = this.apiResource["api.progress.total_result_data"];
    var params = {performance_id: performance_id};
    return $.getJSON(url, params).promise();
  }
})

// view
var PerformanceChoiceView = Backbone.View.extend({
  events: {
    "change select[name='performance_id']": "onPerformanceChange"
  }, 
  initialize: function(opts){
    this.datastore = opts.datastore;
    this.apiService = opts.apiService;
    this.messageView = opts.messageView;
    this.$performance_id = this.$el.find("select[name='performance_id']");
  }, 
  onPerformanceChange: function(){
    var performance_id = this.$performance_id.find(":selected").val();
    var self = this;
    this.apiService.getPerformanceData(performance_id)
      .fail(function(s, msg){self.messageView.error(s.responseText)})
      .done(function(data){
        if(data.status != "success"){
          self.messageView.error(data.message);
        }
        self.datastore.updateFromPerformanceChangeApi(data.data);
      });
  }
});

var DescribeTotalResultView = Backbone.View.extend({
  initialize: function(opts){
    this.datastore = opts.datastore;
    this.apiService = opts.apiService;
    this.messageView = opts.messageView;

    this.total_result = this.datastore.get("total_result");
    this.total_result.bind("*update.total_result", this.updateTotalResult, this);

    this.$total = this.$el.find("#desc_total");
    this.$total_qr = this.$el.find("#desc_total_qr");
    this.$total_other = this.$el.find("#desc_total_other");
    this.$qr_printed = this.$el.find("#desc_qr_printed");
    this.$qr_unprinted = this.$el.find("#desc_qr_unprinted");
  }, 
  updateTotalResult: function(){
    var total_result = this.datastore.get("total_result");
    this.$total.text(total_result.get("total"));
    this.$total_qr.text(total_result.get("total_qr"));
    this.$total_other.text(total_result.get("total_other"));
    this.$qr_printed.text(total_result.get("qr_printed"));
    this.$qr_unprinted.text(total_result.get("qr_unprinted"));
  }
});

var DescribeTimeView = Backbone.View.extend({
  initialize: function(opts){
    this.datastore = opts.datastore;
    this.apiService = opts.apiService;
    this.messageView = opts.messageView;
    
    this.datastore.bind("change:current_time", this.updateCurrentTime, this);
    this.$current_time = this.$el.find("#desc_current_time");
  }, 
  updateCurrentTime: function(){
    // this is string not calculatable value
    this.$current_time.text(this.datastore.get("current_time"));
  }
});