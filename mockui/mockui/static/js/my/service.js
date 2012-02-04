var service = (function(){
    var DragWidgetService = {
        create_dropped_widget: function(widget_name){
            var w = $("<div>").draggable({revert:true});

            w.addClass("dropped-widget").addClass("float-left");
            w.css("background-color", "orange").text(widget_name);

            // attach close button
            var close_button = $("<a class='close'>")
            w.append(close_button);
            
            // attach edit button
            var edit_button = $("<a class='edit'>").attr("rel", "#overlay")
            w.append(edit_button);
            return w
        }, 
        get_elt: function(widget_name){
            return $("#widget_palet #@name@".replace("@name@", widget_name))
        }
    };

    var ElementInfoService = {
        get_name: function(element){ return element.attr("id");}
    };

    var DroppableSheetService = (function(){
        var _is_close_event_attached = false
        var default_opt = {
            dropable_class: "droppable", 
            hover_class: "ui-state-hove", 
        };
        return {
            get_elt: function(block_name){
                return $("#selected_layout #@name@".replace("@name@", block_name))
            }, 
            attach_droppable: function(layout, opt){
                var params = opt || default_opt
                var blocks = layout.blocks();
                blocks.addClass(params.droppable_class);
                blocks.droppable({
                    hoverClass: params.hover_class, 
			        drop: function( ev, ui ) {
                        DroppableSheetViewModel.on_drag_and_drop(ui.draggable, this);
			        }
                });
            }, 
            append_widget: function(where, block_name, widget_name, widget){
                var manager = Resource.manager;
                manager.add_widget(block_name, widget, {widget_name: widget_name});
                return where.append(widget)
            }
        };
    })();

    var WidgetElementService = (function(){
        var _is_close_event_attached = false
        var attach_widget_delete_event = function(){
            if (!_is_close_event_attached){
                $(".dropped-widget .close").live("click", function(){
                    var widget_elt = $(this).parent(".dropped-widget");
                    DroppedWidgetViewModel.on_close_button_pushed(widget_elt);
                });
                _is_close_event_attached = true;
            }
        };
        var delete_widget = function(w){
            $(w).remove();
        };
        return {
            attach_widget_delete_event: attach_widget_delete_event, 
            delete_widget: delete_widget, 
            get_edit_button:  function(w){return $(w).find(".edit")}
        };
    })();
    
    var SelectLayoutService = (function(){
        var _close_dialog = null;
        return {
            attach_click_after_event: function(elemts, selector){
                $(selector).live("click", function(ev, data){
                    SelectLayoutService.close_dialog(this)
                });
            },
            attach_overlay_event: function(open_trigger, close_trigger){
                // problem: select layout dialog is also getting via ajax request?(same for selecting widget dialog)
                //
                var elt = $(open_trigger);
                elt.overlay({
                    closeOnClick: true,
                    closeOnESC: true, 
                    onBeforeLoad: function(){
                        _close_dialog = elt.data("overlay").close;
                        if(_close_dialog == null){
                            throw "overlay close() is not found(in select layout dialog)"
                        }
                        SelectLayoutViewModel.on_dialog(this.getOverlay());
                    }
                });
            }, 
            close_dialog: function(caller){
                var close_fn = _close_dialog;
                return SelectLayoutViewModel.on_selected(caller, close_fn);
            }, 
            layout_name: function(expr){
                return $($(expr).find(".info")[0]).attr("layout_name")
            }, 
            get_elt: function(layoutname){
                var expr = "#peace1 div[name=@name@]".replace("@name@", layoutname);
                return $(expr)[0];
            }
        };
    })();

    var WidgetDialogService = (function(){
        var _close_dialog = null;
        var _widget_elt = null;
        var _widget_name = null;
        return {
            // clean_dialog: function(){
            //     $(".dialog_overlay .contentWrap").children().remove();
            // }, 
            finish_dialog: function(caller){
                return WidgetDialogViewModel.on_selected(
                    caller,
                    _widget_name,
                    _widget_elt,
                    _close_dialog
                );
            }, 
            attach_overlay_event: function(widget_name, dropped_widget, attach_source){ //widget_nameで分岐
                var widget_elt = dropped_widget;
                var opts = {
                    closeOnClick: true,
                    closeOnESC: true, 
                    onBeforeLoad: function() {
			            // grab wrapper element inside content
			            var wrap = this.getOverlay().find(".contentWrap");
			            // load the page specified in the trigger
                        var manager = Resource.manager;
                        var block_name = manager.block_name(widget_elt);
                        var orderno = manager.orderno(block_name, widget_elt);
                        var url =  api.load_widget_url(block_name, orderno);

                        // set widget info                        
                        _close_dialog = attach_source.data("overlay").close;
                        _widget_name = widget_name,
                        _widget_elt = widget_elt;

                        if(_close_dialog == null || _widget_elt == null || _widget_elt == null){
                            throw "overlay close() is not found(in select widget dialog)"
                        }



                        var dialog_elt = wrap.load(url)
                        WidgetDialogViewModel.on_dialog(dialog_elt, widget_name, widget_elt);
		            }
                };
                $(attach_source).overlay(opts);
            }
        };
    })();
    

    var VisibilityService = {
        data_packed_widget: function(elt){
            $(elt).addClass("data-packed").css("background-color", "blue");
            return elt;
        }, 
        unhidden: function(expr){
            var elt = $(expr);
            if(elt.hasClass("hidden")){
                $(expr).removeClass("hidden");
            } else{
                elt.show();
            }
        }, 
        hidden: function(expr){
            var elt = $(expr);
            if(elt.hasClass("hidden")){
                $(expr).addClass("hidden");
            } else{
                elt.hide();
            }
        }, 
        attach_selected_highlight_event: function(expr){
	        $(expr+":not(.sexprcted)").live("mouseenter",function(){
	            $(this).addClass("selected");
	        });
            
	        $(".selected").live("mouseleave",function(){
	            $(this).removeClass("selected");
	        });
        }
    };

    var ApiService = {
        save_layout: function(layout_name){
            return api.save_layout(layout_name);
        }, 
        load_layout: function(layout_name){
            Resource.refresh();
            return api.load_layout(layout_name);
        }, 
        save_block: function(block_name, widget_name, dropped_widget){
            var manager = Resource.manager;
            var orderno = manager.orderno(block_name, dropped_widget);
            return api.save_block(block_name, widget_name, orderno);
        }, 
        move_block: function(draggable, droppable){
            // todo: fixme
            var manager = Resource.manager;
            var old_block = manager.block_name(draggable);
            var old_orderno = manager.orderno(old_block, draggable);
            var block_name = ElementInfoService.get_name($(droppable));
            manager.move_widget(old_block, block_name, draggable);
            var orderno = manager.orderno(block_name, draggable);
            return api.move_block(old_block, old_orderno, block_name, orderno);
        }, 
        delete_widget: function(widget_element){
            var manager = Resource.manager;
            var block_name = manager.block_name(widget_element);
            var orderno = manager.orderno(block_name, widget_element);
            return api.delete_widget(block_name, orderno);
        }, 
        save_data: function(widget_name, widget_elt, data){
            console.log("---save_data!--");
            console.log(widget_name);
            console.dir(data);
        }
    };

    var ElementLayoutService = {
        default_layout: function(selectors){
            var l_list  = _.map(selectors, function(e){return new layouts.Candidate(e)});
            var cl = layouts.CandidateList.apply(this, l_list);
            layouts.DefaultLayout.candidate_layout(cl);
        }, 
        swap_child: function(parent, new_child){
            $(parent).append(new_child);
            $($(parent).children()[0]).remove();
        }, 
        replace_inner: function(target, html){
            $(target)[0].innerHTML = html;
        }
    };

    var FetchDialogDataService = {
        image_widget: function(choiced_elt, widget_elt){
            return {imagefile: $(choiced_elt).attr("src")};
        }
    }
    
    return {
        DragWidgetService: DragWidgetService, 
        ElementInfoService: ElementInfoService,
        DroppableSheetService: DroppableSheetService,
        SelectLayoutService: SelectLayoutService,
        WidgetDialogService: WidgetDialogService,
        VisibilityService: VisibilityService,
        ApiService: ApiService,
        ElementLayoutService: ElementLayoutService, 
        WidgetElementService: WidgetElementService, 
        FetchDialogDataService: FetchDialogDataService
    };
})();