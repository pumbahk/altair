var widget = (function(){
    var env = {};
    var base_opt = {
        dialog: null, 
        widget_name: null, 
        where: null,  //widget self
        get_data: function(){}, 
        set_data: function(){}, 
        close_dialog: function(){} 
        // attach_hightlight: function(){}, 
        // attach_managed: function(){}
    };

    var configure = function(opt){
        _.extend(base_opt, opt);
        _.each(env, function(m){
            if(!!m.opt){
                _.extend(m.opt, base_opt);
            }
        });
            
    }

    var get = function(widget_name){
        return env[widget_name] || env[widget_name.replace("_widget", "")]
    };

    var include = function include(name, val){
        if(!!env[name]){
            throw "nameconflict: @s@ is already defined ".replace("@s@", name);
        }            
        if(!!env["create_context"] || env["opt"]){
            console.warn( "nameconflict: `create_with_event' or opt are already defined")
        }
        env[name] = val;

        var default_opt = _.extend({}, base_opt);
        env[name].opt = default_opt;
        env[name].create_context= function(opt){
            // env local variable
            var we = _.extend(env[name].opt, opt);
            if(!we.dialog)
                throw("dialog is not found");
            if(!we.where)
                throw("where is not found");
            if(!we.widget_name)
                throw("widget_name is not found");
            return we;
        };
        return env;
    };


    return {env: env, 
            include: include,
            get: get,
            configure: configure, 
           };
})();
