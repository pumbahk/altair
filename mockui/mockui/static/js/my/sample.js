var Resource = (function(){
    var current_state = null;
    var _manager = manager.DataManager();
    var _hmanager = manager.HeightManager();
    return {
        current_state: current_state, 
        hmanager: _hmanager, 
        manager: _manager, 
        refresh: function(){
            _manager.refresh();
            _hmanager.refresh();
        }
    };
})()


var SelectLayoutViewModel = (function(){
    var _selector = {
        candidate: ".simple_overlay .candidate",
        event_farm: "#selected", 
        overlay_trigger: "div[rel]", 
        overlay_close_trigger: ".candidate", 
        has_selected_highlight: ".candidate", 
        selected_id: "#wrapped", 
        layout_targets: ["#wrapped ", "#wrapped1 ", "#wrapped2 "]
    };

    var on_drawable = function(){
        var dfd = reaction.AfterDrawableSelectLayout.start()
        return dfd.resolveWith(dfd, [_selector])
    };

    var on_dialog = function(dialog_elt){
        // hook when dialog is created.
        console.log("dialog created");
    };
    
    var on_selected_with_api = function(layout_name, cont){
        var selected_elt = service.SelectLayoutService.get_elt(layout_name);
        Resource.layout = selected_elt;
        var params = {
            prefix: "selected", 
            selected_elt: selected_elt, 
            layout_name:  layout_name, 
            after_api_cont: cont,
        }
        var ctx = _.extend({}, _selector, params)
        var dfd = reaction.AfterSelectLayout.start();
        return dfd.resolveWith(dfd, [ctx]);   
    };

    var on_selected = function(selected_elt, close_fn){
        close_fn() // close_dialog
        Resource.layout = selected_elt;
        var layout_name = service.SelectLayoutService.layout_name(selected_elt);
        service.ApiService.save_layout(layout_name);

        var params = {
            prefix: "selected", 
            selected_elt: selected_elt, 
            layout_name:  layout_name, 
        }

        var ctx = _.extend((ctx || {}), _selector, params)
        var dfd = reaction.AfterSelectLayout.start()
        return dfd.resolveWith(dfd, [ctx]);
    };
    
    return {
        on_drawable: on_drawable, 
        on_dialog: function(){}, 
        on_selected: on_selected, 
        on_selected_with_api: on_selected_with_api
    };
})();


var DraggableWidgetViewModel = (function(){
    var _selector = {
        draggable: ".widget"
    };

    var on_drawable = function(){
        // add widget
        service.VisibilityService.attach_selected_highlight_event(".widget");
		$(_selector.draggable).draggable({revert: true});
    };
    return {
        on_drawable: on_drawable
    }
})();

var DroppableSheetViewModel = (function(){
    var _selector = {
        dropped_sheet: "#selected_layout", 
        sheet_block: "#wrapped", 
        layout_target: "#wrapped", 
        row_block: ".block-row" //
    };
    var on_drawable = function(selected_html){
        var selected_layout = new layouts.Candidate(_selector.layout_target);
        var params = {selected_html: selected_html, 
                      selected_layout: selected_layout};
        var ctx = _.extend({}, _selector, params);
        var dft = reaction.AfterDrawableDroppableSheet.start();
        dft.resolveWith(dft, [ctx]);
    };
    
    var on_drag_and_drop = function(draggable, droppable){
        if($(draggable).hasClass("widget")){
            var dfd = reaction.DragWidgetFromPalet.start();
            return dfd.resolveWith(dfd, [draggable, droppable]);
        }else if($(draggable).hasClass("dropped-widget")){
            var dfd = reaction.DragWidgetFromInternalBlock.start();
            return dfd.resolveWith(dfd, [draggable, droppable]);
        }
    };

    var on_append_with_api = function(dfd, data){
      // [{widgets:[{data:{},
      //             widget_name:"dummy_widget1"}],
      //   block_name:"selected_left"},
      //  {widgets:[{data:{},
      //             widget_name:"image_widget"}],
      //   block_name:"selected_header"}
      // ]
      dfd.done(function(){
          _.each(data, function(saved_block){
              var block_name = saved_block["block_name"];
              var droppable = service.DroppableSheetService.get_elt(block_name);
              _.each(saved_block["widgets"], function(widget_info){
                  var widget_name = widget_info.widget_name;
                  var draggable = service.DragWidgetService.get_elt(widget_name);
                  var data = widget_info.data;
                  reaction.DragWidgetFromPaletWithApi.delegated_with_args(dfd, [draggable, droppable, data]);
              });
          });
      })
    };

    return {
        on_drag_and_drop: on_drag_and_drop, 
        on_append_with_api: on_append_with_api, 
        on_drawable: on_drawable
    };
})();

var DroppedWidgetViewModel = {
    on_drawable: function(){
        service.VisibilityService.attach_selected_highlight_event(".dropped-widget");
    }, 
    on_close_button_pushed: function(widget_elt){
        var dfd =  reaction.WidgetCloseButtonPushed.start()
        dfd.resolveWith(dfd, [widget_elt]);
    }
};

var WidgetDialogViewModel = (function(){
    var _selector = null
    var on_dialog = function(dialog_elt, widget_name, widget_elt){
        var wmodule = widget.get(widget_name)
        if(!!wmodule){
            var we = widget.create_widget_event({
                dialog: dialog_elt, 
                where: widget_elt, 
                widget_name: widget_name
            });
            setTimeout(function(){wmodule.on_dialog(we);}, 0);
        }
    };
    var on_selected = function(choiced_elt, widget_name, widget_elt, close_fn){
        var wmodule = widget.get(widget_name)
        if(!!wmodule){
            var we = widget.create_widget_event({
                dialog: dialog_elt, 
                where: widget_elt, 
                widget_name: widget_name, 
                close_dialog: close_fn
            });
            vm.module.on_selected(we);
        }

        var params = {
            widget_name: widget_name, 
            choiced_elt: choiced_elt, 
            widget_elt: widget_elt, 
        }
        console.log("dialog selected");
        var dfd = reaction.WidgetDataSubmit.start();
        return dfd.resolveWith(dfd, [params])
    };
    return {
        // on_droppable_widget_created: on_droppable_widget_created, 
        on_dialog: on_dialog, 
        on_selected: on_selected
    }
})();

var STAGE = {
    NEW : 0,
    LAYOUT_SELECTED : 1,
    WIDGETS_SELECTED : 2
};

function loading_data(){
    $.getJSON("/sample/api/load/stage").done(function(data){
        //
        //
        Resource.current_state = data.stage; //
        var dfd = $.Deferred();
        // if(data.stage >= STAGE.NEW){}
        if(data.stage == STAGE.LAYOUT_SELECTED){
            dfd.done(function(){
                var layout_name = data["layoutname"];
                SelectLayoutViewModel.on_selected_with_api(layout_name);
            });
        }
        if(data.stage >= STAGE.WIDGETS_SELECTED){
            dfd.done(function(){
                var layout_name = data["layoutname"];
                SelectLayoutViewModel.on_selected_with_api(
                    layout_name, 
                    function(){
                        var serialized_data = data["context"]
                        DroppableSheetViewModel.on_append_with_api(dfd, serialized_data);
                    });
            });
        }
        return dfd.resolve()
    });
};

$(function(){
    widget.configure({
        dialog: null, //dynamic bind
        widget_name: null, //dynamic bind
        where: null, //dynamic bind
        close_dialog: function(){}, //dynamic bind 
        get_data: function(e){return Resource.manager.find(e)}, 
        set_data: function(e, data){
            var block_name = manager.block_name(e);
            Resource.manager.update_data(block_name, e, data);
        }, 
        attach_highlight: service.VisibilityService.attach_hightlight
    });
    $.when(SelectLayoutViewModel.on_drawable(), 
           DraggableWidgetViewModel.on_drawable(), 
           DroppedWidgetViewModel.on_drawable())
        .done(loading_data);
});