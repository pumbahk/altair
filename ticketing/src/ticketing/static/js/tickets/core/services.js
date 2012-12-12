if (!window.core)
    window.core = {};

(function(core){
    var isCallable = function(t){
        return typeof t === "function";
    };

    core.InspectService = {
        isCallable: isCallable
    };

    core.ApiService = {
        rejectIfStatusFail: function(fn){
            return function(data){
                if (data && data.status){
                    return fn? fn(data) : data;
                }else {
                    return $.Deferred().rejectWith(this, [{responseText: "status: false, "+data.message+arguments[0]}, ]);
                }
            };
        }, 
        asGetFunction: function(url_or_fn){
            return isCallable(url_or_fn) ? url_or_fn : _.bind($.get, $, url_or_fn);
        }, 
        asPostFunction: function(url_or_fn){
            return isCallable(url_or_fn) ? url_or_fn : _.bind($.post, $, url_or_fn);
        }
    };
})(window.core);