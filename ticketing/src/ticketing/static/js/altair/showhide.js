// require jquery
// side-effect jquery.altair.showhide
// rdepends: ./spinner.js


(function($){
    if(!$.altair){
        $.altair = {};
    }

    var _strict_get = function(params, k){
        var v = params[k]
        if(!v){
            throw k +" is not found in params";
        }
        return v;
    }

    var ShowHideFactory = function(opts){
        this.name = _strict_get(opts, "name");
        this.createElement = _strict_get(opts, "createElement");
    };

    ShowHideFactory.prototype.getData = function getData($e, cont){
        var item = $e.data(this.name);
        if (!!item){
            if(!!cont){ cont(item);}
            return item;
        }
        return this.create($e)
    };
    ShowHideFactory.prototype.create = function create($e, cont){
        var item = this.createElement();
        if(!!cont){cont(item);}
        $e.append(item);
        $e.data(this.name, item);
        return item;
    };
    ShowHideFactory.prototype.show = function show($e){
        return this.getData($e,function(item){item.show();})
    };
    ShowHideFactory.prototype.hide = function hide($e){
        return this.getData($e,function(item){item.hide();})
    };
    ShowHideFactory.prototype.destroy = function destroy($e){
        var item = $e.data(this.name);
        if(!!item){
            item.remove();
            $e.data(this.name, null);
        }
    };
    $.altair.showhide = ShowHideFactory;
})(jQuery);