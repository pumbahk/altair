
if(!widget){
    throw "widget module is not found";
}

/* we argument has
widget.configure({
    dialog: null, //dynamic bind
    widget_name: null, //dynamic bind
    where: null, //dynamic bind
    get_pk: function(e){
    }, 
    get_data: function(e){
    }, 
    set_data: function(e, data){
    }, 
    attach_highlight: function(e){
    }, 
    attach_managed: function(e){
    }, 
    get_orderno: function(e){
    }
});
*/

(function(widget){
    var opt = {} //widget local variable
    var load_page = function(we){
        var pk = we.get_pk(we.where);
        var url = "/api/widget/topic/dialog";
        var params = {};
        if(!!pk){
            params["pk"] = pk;
        }
        url += "?" + $.param(params);
        return we.dialog.load(url);
    };

    form_change_api_url = "./api/form?";
    var on_dialog = function(we){
        $("#submit").click(function(){we.finish_dialog(this);});

        //対応したformに変更
        // var self = this;
        // $("#topic_type").change(function(){
        //     $(this).parent("tbody").load(form_change_api_url+$.param(self.collect_data(we)));
        // })
    };

    var on_close = function(we){
    };

    var collect_data = function(we, choiced_elt){
        var root = $(we.dialog);
        return {"kind": root.find("#kind").val(), 
                "subkind": root.find("#subkind").val(), 
                "topic_type": root.find("#topic_type").val(), 
                "display_count": root.find("#display_count").val(), 
                "display_global": !!root.find("#display_global").attr("checked"), 
                "display_page": !!root.find("#display_page").attr("checked"), 
                "display_event": !!root.find("#display_event").attr("checked")
               };
    };
    return widget.include("topic", {
        load_page: load_page, 
        on_dialog: on_dialog, 
        on_close: on_close, 
        collect_data: collect_data, 
    });
})(widget); 
