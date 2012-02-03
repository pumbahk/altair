var log = function(mes){
    console.log("================")
    console.log(mes);
    console.log("================")
};

// var _with_log = function(data){
//     log(data);
//     return data;
// };

var _with_log = function(data){
    return data;
};

var api = (function(){
    var _save_layout = function(layout_name){
        return $.post("/api/save/layout", {layout_name:layout_name}).then(_with_log);
    };
    var _load_layout = function(prefix){
        return $.get("/api/load/layout", {prefix: prefix}).then(_with_log);
    };
    var _save_block = function(block_name, widget_name, orderno){
        var params = {
            block_name: block_name, 
            widget_name: widget_name, 
            orderno: orderno
        }
        return $.post("/api/save/block",  params).then(_with_log);
    };
    var _load_block = function(block_name, orderno){
        var params = {
            block_name: block_name, 
            orderno: orderno
        }
        return $.get("/api/load/block",  params).then(_with_log);
    };
    var _load_widget_url = function(block_name, orderno){
        var params = {
            block_name: block_name, 
            orderno: orderno
        }
        return "/api/load/widget"+"?"+$.param(params)
    };

    var _move_block = function(old_block, old_orderno, block_name, orderno){
        var params = {
            old_block: old_block, 
            old_orderno: old_orderno, 
            block_name: block_name, 
            orderno: orderno
        }
        return $.post("/api/move/block",  params).then(_with_log);
    };

    var _delete_widget = function(block_name, orderno){
        var params = {
            block_name: block_name, 
            orderno: orderno
        }
        return $.post("/api/delete/widget", params).then(_with_log);
    };

    return {
        save_layout: _save_layout,
        load_layout: _load_layout, 
        save_block: _save_block, 
        load_block: _load_block, 
        load_widget_url: _load_widget_url, 
        move_block: _move_block, 
        delete_widget: _delete_widget
    };
})();