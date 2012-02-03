var reaction = (function(){
    var Reaction = function(opt){
        // opts: {react: fn, 
        //        side_effect: fn
        //        after_that: fn}}
        //
        var react = opt.react;
        var action = function(){
            var arguments_ = arguments;
            if(!!opt.side_effect){
                setTimeout(function(){
                    return opt.side_effect.apply(this,arguments_)
                },0);
            }
            return opt.react.apply(this,arguments)
        };
        var delegated = function(dfd, cont){
            dfd.done(action)
            if(!!cont){
                dfd.done(cont);
            }
            // if(!!opt.after_that){
            //     dfd = dfd.done(opt.after_that);
            // }
            return dfd.promise();
        };

        var delegated_with_args = function(dfd, args, cont){
            dfd.done(function(){
                return action.apply(dfd, args);
            });

            if(!!cont){
                dfd.done(cont);
            }


            // if(!!opt.after_that){
            //     dfd = dfd.done(opt.after_that);
            // }
            return dfd.promise();
        }
        var start = function(cont){
            var dfd = $.Deferred()
            delegated(dfd, cont);
            return dfd;
        }
        return {
            start: start, 
            action: action, 
            delegated: delegated, 
            delegated_with_args: delegated_with_args
        }
    };

    // layout select action
    var AfterDrawableSelectLayout = Reaction({
        react: function(ctx){
            service.SelectLayoutService.attach_click_after_event(
                ctx.event_farm, 
                ctx.candidate
            );
            service.SelectLayoutService.attach_overlay_event(
                ctx.overlay_trigger, 
                ctx.overlay_close_trigger
            );
        }, 
        side_effect: function(ctx){
            service.ElementLayoutService.default_layout(ctx.layout_targets);
            service.VisibilityService.unhidden(ctx.selected_id);
        }
    });


    var AfterSelectLayout = Reaction({
        react: function(ctx){
            var dfd = service.ApiService.load_layout(ctx.prefix, ctx.layout_name).done( // todo fix
                DroppableSheetViewModel.on_drawable
            )
            if(!!ctx.after_api_cont){
                dfd.done(ctx.after_api_cont);
            }
            return dfd
        }, 
        side_effect: function(ctx){
            // swap selected example 
            var new_selected = $.clone(ctx.selected_elt);
            service.ElementLayoutService.swap_child(ctx.event_farm, new_selected);
        }
    });


    // droppable sheet
    var AfterDrawableDroppableSheet = Reaction({
        react: function(ctx){
            var dfd = $.Deferred()
            dfd.done(function(){
                // 挿入されたwidgetの表示が気に食わないので後で書きなおすかも？
                service.ElementLayoutService.replace_inner(
                    ctx.dropped_sheet, ctx.selected_html
                );
            });
            dfd.done(function(){
                service.DroppableSheetService.attach_droppable(ctx.selected_layout);
            });
            dfd.resolve();
        },
        side_effect: function(ctx){
            service.WidgetElementService.attach_widget_delete_event();
            var cl = layouts.CandidateList(ctx.selected_layout);
            layouts.DefaultLayout.selected_layout(cl);
        }
    });

    var WidgetCloseButtonPushed = Reaction({
        react: function(widget_element){
            if(confirm("このwidgetを消します。良いですか？")){
                service.ApiService.delete_widget(widget_element).done(
                    function(){
                        service.WidgetElementService.delete_widget(widget_element);
                    });
                // call delete api!! fixme:
            }
        }
    });

    var DragWidgetFromPalet = Reaction({
        react: function(draggable, droppable){
            var widget_name = service.ElementInfoService.get_name($(draggable));
            var dropped_widget = service.DragWidgetService.create_dropped_widget(widget_name);

            var edit_button = service.WidgetElementService.get_edit_button(dropped_widget);
            service.WidgetDialogService.attach_overlay_event(widget_name, dropped_widget, edit_button);

            var block_name = service.ElementInfoService.get_name($(droppable));
            service.DroppableSheetService.append_widget($(droppable), block_name, widget_name, dropped_widget);
            service.ApiService.save_block(block_name, widget_name, dropped_widget);
        }
    });

    var DragWidgetFromPaletNoSaveApi = Reaction({ //almost same DragWidgetFromPalet
        react: function(draggable, droppable){
            var widget_name = service.ElementInfoService.get_name($(draggable));
            var dropped_widget = service.DragWidgetService.create_dropped_widget(widget_name);
                        
            var edit_button = service.WidgetElementService.get_edit_button(dropped_widget);
            service.WidgetDialogService.attach_overlay_event(widget_name, dropped_widget, edit_button);

            var block_name = service.ElementInfoService.get_name($(droppable));
            service.DroppableSheetService.append_widget($(droppable), block_name, widget_name, dropped_widget);
        }
    });

    var DragWidgetFromInternalBlock = Reaction({
        react: function(draggable, droppable){
            service.ApiService.move_block(draggable, droppable)
                .done(function(){$(droppable).append(draggable)});
        }, 
        // side_effect: function(draggable, droppable){
        //     $(droppable).append(draggable);
        // }
    });

    var WidgetDataSubmit = Reaction({
        react: function(ctx){
            var manager = Resource.manager;
            var block_name = manager.block_name(ctx.widget_elt);
            var fetch_data_fn = service.FetchDialogDataService[ctx.widget_name];
            var data = fetch_data_fn(ctx.choiced_elt, ctx.widget_elt);            
            Resource.manager.update_data(block_name, ctx.widget_elt, data);
            service.ApiService.save_data(ctx.widget_name, ctx.widget_elt, data);
            service.VisibilityService.data_packed_widget(ctx.widget_elt);
        }
    });
    // widget dialog 
    return {
        Reaction: Reaction, 
        AfterDrawableSelectLayout: AfterDrawableSelectLayout, 
        AfterSelectLayout: AfterSelectLayout, 
        AfterDrawableDroppableSheet: AfterDrawableDroppableSheet, 
        WidgetCloseButtonPushed: WidgetCloseButtonPushed, 
        DragWidgetFromPalet: DragWidgetFromPalet, 
        DragWidgetFromPaletNoSaveApi: DragWidgetFromPaletNoSaveApi, 
        DragWidgetFromInternalBlock: DragWidgetFromInternalBlock, 
        WidgetDataSubmit: WidgetDataSubmit
    };
})();