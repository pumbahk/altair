var manager = (function(){
    var _i = 0;
    var keygen = function(){var r = _i; _i++; return String(r)};

    var DataManager = function(){
        var _D = {}
        var _RD = {}
        var _normalize = function(elt){
            if(elt instanceof jQuery){
                return elt;
            } else{
                return $(elt);
            }
        };

        var _to_key = function(elt){
            var jqobj = _normalize(elt);
            var k = jqobj.attr("uid:");
            if(!k){
                var k = keygen();
                jqobj.attr("uid:", k);
            } 
            return k;
        };

        var _get_block = function(block_name){
            if (!_D[block_name]){
                _D[block_name] = [];
            }
            return _D[block_name];
        }

        var _find_info = function(block_name, elt){
            var k = _to_key(elt);
            var arr = _get_block(block_name);
            for (var i=0, j=arr.length;i<j;i++){
                if(!!arr[i]){
                    if(arr[i].uid == k){
                        return {block: arr,  i: i}
                    }
                }
            }
            throw"widget not found";            
        }
        var _delete_elt = function(block_name, elt){
            var info = _find_info(block_name, elt);
            delete info.block[info.i];
        };

        var _get_orderno = function(block_name, elt){
            var arr = _get_block(block_name);
            var k = _to_key(elt);
            var orderno = 0;

            for (var i=0, j=arr.length;i<j;i++){
                if(!!arr[i]){
                    if(arr[i].uid == k){
                        return orderno;
                    }
                    orderno++;
                }
            }
            throw "widget not found(orderno)";            
        };

        var _add_widget = function(block_name, elt, data){// data  is optional
            var k = _to_key(elt);
            var val = {
                elt: elt, 
                uid: k,
            };
            if(!!data){
                _.extend(val, data);
            }
            _get_block(block_name).push(val);
            _RD[k] = block_name;
        };        
        return {
            refresh: function(){
                _D = {};
                _RD = {};
            }, 
            find: function(elt){
                var block_name = _RD[_to_key(elt)];
                var info = _find_info(block_name, elt);
                return info.block[info.i];
            }, 
            update_data: function(block_name, elt, data){
                var info = _find_info(block_name, elt)
                return _.extend(info.block[info.i], data);
            }, 
            move_widget: function(old_block, block_name, elt){
                _add_widget(block_name, elt);
                _delete_elt(old_block, elt)
            }, 
            add_widget: _add_widget, 
            block_name:  function(elt){
                return _RD[_to_key(elt)];
            }, 
            orderno: _get_orderno, 
            clear: function(){
                _D = {}
                _RD = {}
            }
        }
    };

    return {
        "DataManager": DataManager, 
    };
})();