
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
    get_display_order: function(e){
    }
});
*/

(function(widget){
    var opt = {} //widget local variable
    var load_page = function(we){
        var pk = we.get_pk(we.where);
        var url = "/api/widget/topcontent/dialog";
        var params = {};
        if(!!pk){
            params["pk"] = pk;
        }
        params["page"] = get_page();
        url += "?" + $.param(params);
        return we.dialog.load(url);
    };

    form_change_api_url = "./api/form?";
    var on_dialog = function(we){
        we.bind_retry(we, 10, 1.43, 15, 
                      function(){return $("#topcontent_submit")}, 
                      function(elt){elt.click(function(){we.finish_dialog(this);});}
                     )();

        //対応したformに変更
        // var self = this;
        // $("#topcontent_type").change(function(){
        //     $(this).parent("tbody").load(form_change_api_url+$.param(self.collect_data(we)));
        // })
    };

    var on_close = function(we){
    };

    var collect_data = function(we, choiced_elt){
        var root = $(we.dialog);
        return {"display_type": root.find("#display_type").val(), 
                "display_count": root.find("#display_count").val(), 
                "tag": root.find("#tag").val()};
    };
    return widget.include("topcontent", {
        load_page: load_page, 
        on_dialog: on_dialog, 
        on_close: on_close, 
        collect_data: collect_data, 
    });
})(widget); 
