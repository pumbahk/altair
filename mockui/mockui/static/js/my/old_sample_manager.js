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

    var LayoutManager = (function(color_mapping){
        // todo fix
        var candidate_conf = {
            width: 200, 
            heights: {ratio: {header: 0.25,
                              left: 1.0,
                              center: 1.0,
                              right: 1.0,
                              footer: 0.25}, 
                      base: 200, 
                      unit: "px"}, 
            colors: {
                "header": "gray",
                "left": "blue",
                "center": "green",
                "right": "red",
                "footer": "gray"
            }
        };

        var selected_conf = {
            width: 600, 
            heights: {ratio: {header: 0.25,
                              left: 1.0,
                              center: 1.0,
                              right: 1.0,
                              footer: 0.25}, 
                      base: 300, 
                      unit: "px"}, 
            colors: {
                "header": "gray",
                "left": "blue",
                "center": "green",
                "right": "red",
                "footer": "gray"
            }        
        };

        var defaultColor = {
            "red": "#ffaaaa",
            "green": "#aaffaa",
            "blue": "#aaaaff",
            "gray": "#999"
        };
        if (!color_mapping){
            color_mapping = defaultColor;
        }
        var _get_color = function(color){
            return !!color_mapping[color] ? color_mapping[color] : color;
        };

        var _get_length = function(length, base, unit){
            if(_.isNumber(length)){
                length = base * length;
                if(!!unit){
                    length = String(length)+unit;
                }
            }
            return length;
        };

        return {
            candidate_conf: candidate_conf,
            selected_conf: selected_conf,
            color: _get_color,
            length: _get_length
        }
    })();
    
    var HeightManager = function(){
        current_map = {};
        default_map = {};
        var gensym_c = 0;
        var _to_key = function(elt){
            foo = elt;
            var k = $(elt).data("hid:");
            if(!!k){return k;}
            throw "not managed it (HeightManager)"
        };

        return {
            manage_it: function(row_expr, default_v){
                _.each($(row_expr), function(e){
                    $(e).data("hid:", gensym_c);
                    current_map[gensym_c] = unit.get(default_v); //
                    gensym_c++;
                });
            }, 
            child_to_rowelt: function(row_expr, child){
                return $(child).parent(row_expr);
            }, 
            over_default: function(elt){
                var k = _to_key(elt);
                return default_map[k].val < current_map[k].val;
            }, 
            refresh: function(){
                current_map = {};
                default_map = {};
                gensym_c = 0;
            }, 
            set_default: function(elt, height){
                default_map[_to_key(elt)] = height;
            }, 
            add_current: function(elt, d){
                var k = _to_key(elt);
                console.log("k is "+k);
                var v = current_map[k].add(d);
                current_map[k] = v;
                return v;
            }, 
            sub_current: function(elt, d){
                var k = _to_key(elt);
                var v = current_map[k].sub(d);
                current_map[k] = v;
                return v;
            }, 
            current: function(elt){
                return current_map[_to_key(elt)];
            }
        }
    };
    return {
        DataManager: DataManager, 
        HeightManager: HeightManager, 
        LayoutManager: LayoutManager
    };
})();