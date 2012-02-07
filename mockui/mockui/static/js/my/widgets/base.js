var widget = (function(){
    var env = {};
    var opt = {
        dialog: null, 
        widget_name: null, 
        where: null,  //widget self
        get_data: function(){}, 
        set_data: function(){}, 
        close_dialog: function(){}, 
        attach_hightlight: function(){}, 
        attach_managed: function(){}
    };

    var include = function include(name, val){
        if(!!env[name]){
            throw "nameconflict: @s@ is already used ".replace("@s@", name);
        }            
        env[name] = val;
        return env;
    };

    var configure = function(default_opt){
        _.extend(opt, default_opt);
    }

    var get = function(widget_name){
        n return env[widget_name]
    };
    var create_widget_event = function(opt_){
        var we = _.extend({}, opt, opt_);
        if(!we.dialog)
            throw("dialog is not found");
        if(!we.where)
            throw("where is not found");
        if(!we.widget_name)
            throw("widget_name is not found");
        return we;
    };

    return {env: env, 
            include: include,
            get: get,
            configure: configure, 
            create_widget_event};
})();

