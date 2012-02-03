var Resource = (function(){
    var current_state = null;
    var _manager = manager.DataManager();
    return {
        current_state: current_state, 
        manager: _manager, 
        refresh: function(){
            _manager.refresh();
        }
    };
})()


var SelectLayoutViewModel = (function(){
    var _selector = {
        candidate: ".simple_overlay .candidate",
        event_farm: "#selected", 
        overlay_trigger: "div[rel]", 
        overlay_close_trigger: ".candidate", 
        selected_id: "#wrapped", 
        layout_targets: ["#wrapped", "#wrapped1", "#wrapped2"]
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
    };
    var on_drawable = function(selected_html){
        var selected_layout = new layouts.Candidate("#wrapped");
        var params = {selected_html: selected_html, 
                      selected_layout: selected_layout};
        var ctx = _.extend({}, _selector, params);
        var dft = reaction.AfterDrawableDroppableSheet.start()
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
        // [{
        //     'widgets': ["image_widget"], 
        //     'block_name': 'selected_center'
        //  }, 
        //  {
        //     'widgets': ["dummy_widget"], 
        //     'block_name': 'selected_header'
        //  }]
        _.each(data, function(saved_block){
            var block_name = saved_block["block_name"];
            var droppable = service.DroppableSheetService.get_elt(block_name);
            _.each(saved_block["widgets"], function(widget_info){
                var widget_name = widget_info;
                var draggable = service.DragWidgetService.get_elt(widget_name);
                reaction.DragWidgetFromPaletNoSaveApi.delegated_with_args(dfd, [draggable, droppable]);
            });
        });
    };

    return {
        on_drag_and_drop: on_drag_and_drop, 
        on_append_with_api: on_append_with_api, 
        on_drawable: on_drawable
    };
})();

var DroppedWidgetViewModel = {
    on_close_button_pushed: function(widget_elt){
        var dfd =  reaction.WidgetCloseButtonPushed.start()
        dfd.resolveWith(dfd, [widget_elt]);
    }
};

var WidgetDialogViewModel = (function(){
    var on_dialog = function(dialog_elt, widget_name, widget_elt){
        // fixme
        // dialog_elt.append($("<a class='close'>"));
        dialog_elt.append($("<div>").text("hohohohoho"));
        dialog_elt.css("background-color", "blue");
        console.log("dialog created");
    };
    var on_selected = function(choiced_elt, widget_elt, close_fn){
        // fixme
        service.VisibilityService.data_packed_widget(widget_elt);
        console.log("dialog selected");
        close_fn();
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
    $.getJSON("/api/load/stage").done(function(data){
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
    $.when(SelectLayoutViewModel.on_drawable(), 
           DraggableWidgetViewModel.on_drawable())
        .done(loading_data);
});