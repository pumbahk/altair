var widget = (function(){
    var bind_retry = function(we, a0, d, n, finder, do_something, failback){
        // a0 = 10, d = 1.43, n=15
        // 15, 4949.21343937
        var wait_time = a0; // todo: receive as function argument.
        var iter = function iter(i){
            //console.log(we.canceld)
            if (i > n){
                alert("error: broken widget. please reload")
            }
            var elt = finder();
            if(elt.length <=0){
                wait_time = wait_time * d;
                if(!!failback){
                    failback(elt);
                }
                if(we.canceld){
                    //console.log("canceld");
                    // clean cancel flag and not call cont
                }else{
                    //console.log("retry");
                    setTimeout(function(){iter(i+1)}, wait_time);
                }
            }else {
                //console.log("finished");
                wait_time = a0;
                do_something(elt);
            }   
        }
        return function(){iter(0)};
    };

    var env = {};
    var base_opt = {
        dialog: null, 
        widget_name: null, 
        where: null,  //widget self
        get_block_name: function(e){}, 
        get_orderno: function(e){}, 
        get_data: function(e){}, 
        set_data: function(e, data){}, 
        finish_dialog: function(){}, 
        attach_hightlight: function(e){}, 
        attach_managed: function(e){}, 
        bind_retry: bind_retry
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

        // cancel event
        val.cancel = function(we){
            //console.log("canceld!");
            we.canceld = true;
        };

        env[name] = val;

        var default_opt = _.extend({}, base_opt, env[name].opt);
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

            we.canceld = false;
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
