if (!window.core)
    window.core = {};

core.ConsoleMessage = { //use info, log, warn, error, dir
    success: console.debug, 
    error: console.debug, 
    info: console.debug, 
    warn: console.debug, 
    alert: alert
}

core.MessageInformationView = Backbone.View.extend({
    initialize: function(opts){
        this.$alert = this.$el.find(opts["alert"]);
        this.$info = this.$el.find(opts["info"]);
        this.$error = this.$el.find(opts["error"]);
        this.$success = this.$el.find(opts["success"]);
        this.$messages = this.$el.find(opts["messages"]);
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

core.MessageViewFactory = function(opts){
    var defaults = {
        alert: "#alert_message", 
        info: "#info_message", 
        error: "#error_message", 
        success: "#success_message", 
        messages: ".message"
    };
    return new core.MessageInformationView(_.extend({}, defaults, opts));
}
