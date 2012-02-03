var dialog_manager = manager.DialogOverlayManager();
$(function(){
    var cand_on_selected = new layouts.Candidate("#wrapped");
    var cand_layout0 = new layouts.Candidate("#wrapped1");
    var cand_layout1 = new layouts.Candidate("#wrapped2");
    var cl = layouts.CandidateList(cand_on_selected,cand_layout0, cand_layout1);
    layouts.DefaultLayout.candidate_layout(cl);


	  $(".candidate").live("click", function(ev, data){
        $("#selected").trigger("*update_content*", this);
    });

	  $("div[rel]").overlay({
        close: ".candidate",
        closeOnClick: true,
        closeOnESC: true
    });
    
    $("#selected").data("manager", manager.DataManager())
    $("#selected").live("*update_content*", function(ev, expr){
        var self = this;
        var layout_name = $($(expr).find(".info")[0]).attr("layout_name")
        api.save_layout(layout_name)
            .then(function(){
                api.load_layout("selected")
                    .then(function(selected){
                        $(self).append($.clone(expr));
                        $($(self).children()[0]).remove();
                        return selected;
                    }).then(function(selected){
                        $("#selected_layout")[0].innerHTML = selected;
                        var selected_layout = new layouts.Candidate("#wrapped");
                        var cl = layouts.CandidateList(selected_layout);
                        layouts.DefaultLayout.selected_layout(cl);
                        selected_layout.blocks().addClass("droppable");
                    }).then(function(){
                        // add widget
		                    $( ".widget" ).draggable({revert: true});
		                    $( ".droppable" ).droppable({
                            hoverClass: "ui-state-hover", 
			                      drop: function( ev, ui ) {
                                if($(ui.draggable).hasClass("widget")){
                                    $(this).trigger("*widget_after_drop*", ui.draggable)
                                }else if($(ui.draggable).hasClass("dropped-widget")){
                                    $(this).trigger("*dropped_widget_after_drop*", ui.draggable)
                                }
				                        //$( this ).addClass( "ui-state-highlight" );
			                      }
		                    });
                    });
            });
    });

    
    // after drop event in layout block
    $(".droppable").live("*widget_after_drop*", function(ev, draggable){

        var widget_name = $(draggable).attr("id")
        var dropped_widget = $("<div>").attr("rel", "#overlay").draggable({revert:true})
        dropped_widget.addClass("dropped-widget").addClass("float-left");

        var overlay_maker = (dialog_manager[widget_name] || dialog_manager.dummy_widget);
        overlay_maker(
            dropped_widget, 
            function(){
                var block_name = manager.block_name(dropped_widget);
                var orderno = manager.orderno(block_name, dropped_widget);
                return api.load_widget_url(block_name, orderno);
            });
        
        var manager = $("#selected").data("manager");        
        $(this).append(dropped_widget.css("background-color", "orange")
                       .text(widget_name));
        
        var block_name = $(this).attr("id");
        manager.add_widget(block_name, dropped_widget);
        var orderno = manager.orderno(block_name, dropped_widget);

        api.save_block(block_name, widget_name,  orderno);
    });

    $(".droppable").live("*dropped_widget_after_drop*", function(ev, draggable){
        var self = this;
        var manager = $("#selected").data("manager");
        var old_block = manager.block_name(draggable)
        var old_orderno = manager.orderno(old_block, draggable);
        var block_name = $(self).attr("id");
        manager.move_widget(old_block, block_name, draggable);
        var orderno = manager.orderno(block_name, draggable);
        api.move_block(old_block, old_orderno, block_name, orderno)
            .then(function(){$(self).append(draggable);});
    });
});