if(!widget){
    throw "widget module is not found";
}

(function(widget){

    var load_page = function(we){
        var pk = we.get_pk(we.where);
        var url = "/api/widget/freetext/dialog";
        var params = {};
        if(!!pk){
            params["pk"] = pk;
        }
            url += "?" + $.param(params);
        return we.dialog.load(url);
    };
    var on_dialog = function(we){
        setTimeout(function(){ //todo refactoring
            we.bind_retry(we, 10, 1.43, 15, 
                      function(){return $("#freetext_widget_textarea")}, 
                      function(elt){
                          $("#freetext_widget_textarea").cleditor();
                          var freetext = we.get_data(we.where).freetext;            
                          $("#freetext_submit").click(function(){we.finish_dialog(this);});
                      }
                         )();
        }, 200);
    };

    var on_close = function(we){

    };

    var collect_data = function(we, choiced_elt){
        var root = $(we.dialog)
        return {freetext: root.find("#freetext_widget_textarea").val()}
    };

    return widget.include("freetext", {
        load_page: load_page, 
        on_dialog: on_dialog, 
        on_close: on_close, 
        collect_data: collect_data, 
    });
})(widget); 

