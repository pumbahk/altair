
var service = (function(){
    var DragWidgetService = (function(){

        var fragment = _.template(
(['<div class="dropped-widget">', 
        '<%= content%>', 
        '<a class="close"></a>', 
        '<a class="edit" rel="#overlay"></a>', 
        '</div>', 
  ]).join("\n"));

        return {
            create_dropped_widget: function(widget_name){
                var w = $(fragment({content: widget_name}))
                return w.draggable({revert: true});
            },
            get_elt: function(widget_name){
                return $("#widget_palet #@name@".replace("@name@", widget_name))
            }
        };
    })();

    var ElementInfoService = {
        get_name: function(element){ return element.attr("id");}, 
        get_height: function(element) {return element.css("height");}
    };

    var DroppableSheetService = (function(){
        var _is_close_event_attached = false
        var default_opt = {
            dropable_class: "droppable", 
            hover_class: "ui-state-highlight", 
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
            append_widget: function(where, widget, block_name, widget_name, data){
                var manager = Resource.manager;
                var data = data || {}
                _.extend(data, {widget_name: widget_name})
                manager.add_widget(block_name, widget, data);

                where.append(widget);
                // if(where.find("ul").length==0){
                //     widget.wrap("ul");
                // }
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
        var _finish_dialog = null;
        return {
            attach_click_after_event: function(elemts, selector){
                $(selector).live("click", function(ev, data){
                    SelectLayoutService.finish_dialog(this)
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
                        _finish_dialog = elt.data("overlay").close;
                        if(_finish_dialog == null){
                            throw "overlay close() is not found(in select layout dialog)"
                        }
                        SelectLayoutViewModel.on_dialog(this.getOverlay());
                    }
                });
            }, 
            finish_dialog: function(caller){
                var close_fn = _finish_dialog;
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
        var _dialog_elt = null;
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
                    onClose: function(){
                        setTimeout(function(){
                            //中をdialogの中を空にする
                            WidgetDialogViewModel.on_close(_dialog_elt, _widget_name, _widget_elt);
                        }, 0);
                    }, 
                    onLoad: function(){
                        if(_close_dialog == null || _widget_elt == null || _widget_elt == null){
                            throw "overlay close() is not found(in select widget dialog)"
                        }
                        WidgetDialogViewModel.on_dialog(_dialog_elt, _widget_name, _widget_elt);
                    }, 
                    onBeforeLoad: function() {
			            // grab wrapper element inside content
			            var wrap = this.getOverlay().find(".contentWrap");
			            // load the page specified in the trigger

                        // set widget info                        
                        _close_dialog = attach_source.data("overlay").close;
                        _widget_name = widget_name,
                        _widget_elt = widget_elt;

                        if(_close_dialog == null || _widget_elt == null || _widget_elt == null){
                            throw "overlay close() is not found(in select widget dialog)"
                        }
                        _dialog_elt = WidgetDialogViewModel.on_load_dialog(wrap, _widget_name, _widget_elt);
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
            }
        }, 
        hidden: function(expr){
            var elt = $(expr);
            if(elt.hasClass("hidden")){
                $(expr).addClass("hidden");
            }
        }, 
        unselect: function(elt){
            $(elt).removeClass("selected");
        }, 
        attach_selected_highlight_event: (function(){
            var _cache = {} //cache
            var _first = true
            return function(expr){
                if(!_cache[expr]){
                    // console.log("### "+expr+" ###");
                    _cache[expr] = true; //
	                $(expr+":not(.selected)").live("mouseenter",function(){
	                    $(this).addClass("selected");
	                });
                }
                if (_first){
                    _first = false
	                $(".selected").live("mouseleave",function(){
	                    $(this).removeClass("selected");
	                });
                }
            }
        })()
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
        save_widget: function(widget_name, widget_element, data){
            var manager = Resource.manager;
            var block_name = manager.block_name(widget_element);
            var orderno = manager.orderno(block_name, widget_element);
            return api.save_widget(widget_name, block_name, orderno, data);
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
        }, 
        extend_height: function(wrap, wraph, elth){
            var new_height = calc.add(wraph, elth);
            wrap.css("height", new_height);
        }, 
        remove_children: function(e){
            var e = $(e);
            _.each(e.children(), function(c){$(c).remove();});
        }
    };

    var ChangeHeightService = (function(){
        return {
            manage_it: function(elt){
                var hmanager = Resource.hmanager;
                hmanager.manage_it(elt, "0px"); //fix
            }, 
            extend_if_need: function(where, widget){
                var hmanager = Resource.hmanager;
                var widget_height = unit.get(ElementInfoService.get_height(widget));
                var height = hmanager.add_current(where, widget_height);
                console.log(height);
                if(hmanager.over_default(where)){
                    // extend
                    where.find("div").css("height", height.toString())
                }
            }, 
            reduce_if_need: function(where, widget){
                if(!!_where){
                    var hmanager = Resource.hmanager;
                    var where = hmanager.child_to_rowwhere(where);
                    var widget_height = unit.get(ElementInfoService.get_height(widget));
                    if(hmanager.over_default(where)){
                        var height = hmanager.sub_current(where, widget_height);
                        // reduce
                        where.find("div").css("height", height.toString())
                    } else {
                        hmanager.sub_current(where, widget_height);
                    }
                }
            }
        }
    })();

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
        ChangeHeightService: ChangeHeightService
    };
})();