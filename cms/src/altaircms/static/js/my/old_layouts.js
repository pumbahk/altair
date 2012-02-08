/*
- underscore.js
- jquery.js
*/

// todo: speedup

var layouts = (function(){
    var defaultColor = {
        "red": "#ffaaaa",
        "green": "#aaffaa",
        "blue": "#aaaaff",
        "gray": "#999"
    };

    var Convertor = function(color_mapping){
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
            color: _get_color,
            length: _get_length
        }
    };

    var Candidate = function(wrapped_expr){
        var _get_blocks = function(){
            return $(wrapped_expr+ " > div");
        };

        var _blocks_map = function(args, fn){
            var _blocks = _get_blocks()
            for(var i=0,j=Math.min(args.length, _blocks.length); i<j; i++){
                fn(_blocks[i], args[i]);
            }
        };

        var _get_block_by_suffix = function(suffix){
            var reg = new RegExp("-"+suffix);
            var finder = function(e){return reg.test($(e).attr("class"))}; //using class?
            return _.find(_get_blocks(), finder);
        };

        return {
            blocks: _get_blocks,
            width: function(width){
                $(wrapped_expr).css("width",width);
            },
            if_matched: function(suffix, cont){
                var matched = _get_block_by_suffix(suffix);
                !!matched && cont($(matched));
            }, 
        };
    };

    var CandidateList = function(color_mapping){
        var _member = []
        _.each(arguments, function(e){_member.push(e)});

        if(_member.length > 2 && typeof _member[0] != typeof _member[1]){
            // if color_mapping is passed, sweeps out it from _member;
            _member.shift()
            var _convertor = Convertor(color_mapping);
        } else {
            var _convertor = Convertor();
        }
        var _each_items = function(params, fn){
            for (var p in params){
                if (params.hasOwnProperty(p)){
                    fn(p, params[p]);
                }
            } 
        };

        return {
            add: function(e){
                _.member.push(e);
            },
            each: function(fn){
                _.member.each(fn);
            }, 
            width: function(width){
                _.each(_member, function(e){e.width(width)});
            },
            colors: function(params){
                var self = this
                _each_items(params, function(p, color){
                    self.color(p, color);
                });
            },
            color: function(suffix, color){
                _.each(_member, function(cand){
                    cand.if_matched(suffix, function(m){
                        $(m).css("background-color", _convertor.color(color));
                    });
                });
            },
            height: function(suffix, height, base, unit){
                _.each(_member, function(cand){
                    cand.if_matched(suffix, function(m){
                        var h = _convertor.length(height, base, unit);
                        $(m).css("height", h).attr("height", h);
                    });
                });
            }, 
            heights: function(params, base, unit){
                var self = this
                _each_items(params, function(p, height){
                    self.height(p, height, base, unit);
                });
            }
        }
    };

    var candidate_layout_property = {
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
    var selected_layout_property = {
        width: 700, 
        heights: {ratio: {header: 0.25,
                          left: 1.0,
                          center: 1.0,
                          right: 1.0,
                          footer: 0.25}, 
                  base: 400, 
                  unit: "px"}, 
        colors: {
            "header": "gray",
            "left": "blue",
            "center": "green",
            "right": "red",
            "footer": "gray"
        }        
    };

    // todo refactoring    
    var DefaultLayout = {
        candidate_layout_property: candidate_layout_property, 
        selected_layout_property: selected_layout_property, 
        candidate_layout: function(cl){
            var prop = candidate_layout_property;
            cl.width(prop.width);
            cl.heights(prop.heights.ratio, prop.heights.base, prop.heights.unit);
            cl.colors(prop.colors)
        }, 
        selected_layout: function(cl){
            var prop = selected_layout_property;
            cl.width(prop.width);
            cl.heights(prop.heights.ratio, prop.heights.base, prop.heights.unit);
            cl.colors(prop.colors)
        }
    };

    return {
        "DefaultLayout": DefaultLayout, 
        "Candidate": Candidate,
        "CandidateList": CandidateList
    };
})();

