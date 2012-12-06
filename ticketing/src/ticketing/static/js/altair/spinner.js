// require jquery.js
// altair/showhide.js

// use this
/*
$("#foo").spinner(); // or $("#foo").spinner("start");
$("#foo").spinner("stop");
$("#foo").spinner("destory");
*/
(function($){
    if(!!($.fn.spinner)){
        throw "$.fn.spinner already exists";
    }
    // add-hoc
    var imgsrc = "/static/images/spinner.gif";
    
    var Spinner = new $.altair.showhide({
        name: "spinner", 
        createElement: function(){
            return $("<img spinner-kind='spinner'>").attr("src", imgsrc);
        }
    });

    Spinner.start = Spinner.show;
    Spinner.stop = Spinner.hide;

    $.fn.spinner = function(action){
        if(!action){
            action = "start";
        }
	      this.each(function() {
            Spinner[action].call(Spinner, $(this));
        });        
        return this;
    }
})(jQuery);