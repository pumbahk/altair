if(!widget){
    throw "widget module is not found";
}

(function(widget){
    var 
    load_dialog_url = "/api/widget/freetext/dialog", 
    text_area_expr = "#freetext_widget_textarea", 
    submit_expr = "#freetext_submit", 
    default_body_submit_expr="#freetext_default_body_submit", 
    default_body_choices_expr="#freetext_default_choices", 
    default_body_get_data_url="/api/widget/freetext/api/default_text";
    
    var load_page = function(we){
        var pk = we.get_pk(we.where);
        var url = String(load_dialog_url);
        var params = {};
        if(!!pk){
            params["pk"] = pk;
        }
        url += "?" + $.param(params);
        return we.dialog.load(url);
    };

    var on_default_text_yanked = function(){
        var pk = $(default_body_choices_expr).val();
        $.getJSON(default_body_get_data_url, {"default_body_id": pk}).done(function(data){
            editor = $(text_area_expr).data("cleditor");
            var content = $(editor.doc.body).html();
            console.log(content);
            content += data["data"]["text"];
            $(editor.doc.body).html(content);
            editor.updateTextArea();
        });
    };

    var on_dialog = function(we){
        setTimeout(function(){ //todo refactoring
            we.bind_retry(we, 10, 1.43, 15, 
                      function(){return $(text_area_expr)}, 
                      function(elt){
                          $(text_area_expr).cleditor();
                          var freetext = we.get_data(we.where).freetext;            
                          $(submit_expr).click(function(){we.finish_dialog(this);});
                          $(default_body_submit_expr).click(on_default_text_yanked);
                      }
                         )();
        }, 200);
    };

    var on_close = function(we){

    };

    var collect_data = function(we, choiced_elt){
        var root = $(we.dialog)
        return {freetext: root.find(text_area_expr).val()}
    };

    return widget.include("freetext", {
        load_page: load_page, 
        on_dialog: on_dialog, 
        on_close: on_close, 
        collect_data: collect_data, 
    });
})(widget); 

