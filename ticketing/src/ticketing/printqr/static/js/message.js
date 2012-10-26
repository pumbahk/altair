var message = (function(){
  var defaults = {
    alert: "#alert_message", 
    info: "#info_message", 
    error: "#error_message", 
    success: "#success_message", 
    messages: ".message"
  };

  return function(opts){
    var getopts = function(k){
      return opts[k] || defaults[k];
    };
    
    var MessageInformationView = Backbone.View.extend({
      initialize: function(){
        this.$alert = this.$el.find(getopts("alert"));
        this.$info = this.$el.find("#info_message");
        this.$error = this.$el.find(getopts("error"));
        this.$success = this.$el.find(getopts("success"));
        this.$messages = this.$el.find(getopts("messages"));
      }, 
      _clear: function(){
        this.$messages.hide();
      }, 
      alert: function(message, forcehtml){
        this._clear();
        var updator = !!(forcehtml)? this.$alert.html : this.$alert.text;
        updator.call(this.$alert, message.toString()).show();
      }, 
      info: function(message, forcehtml){
        this._clear();
        var updator = !!(forcehtml)? this.$info.html : this.$info.text;
        updator.call(this.$info, message.toString()).show();
      }, 
      error: function(message, forcehtml){
        this._clear();
        var updator = !!(forcehtml)? this.$error.html : this.$error.text;
        updator.call(this.$error, message.toString()).show();
      }, 
      success: function(message, forcehtml){
        this._clear();
        var updator = !!(forcehtml)? this.$success.html : this.$success.text;
        updator.call(this.$success, message.toString()).show();
      }
    });

    return {
      MessageInformationView: MessageInformationView
    }
  };
})(this);
