// require jquery.js
// static/spin.js
 
/*
You can now create a spinner using any of the variants below:
 
$("#el").spin(); // Produces default Spinner using the text color of #el.
$("#el").spin("small"); // Produces a 'small' Spinner using the text color of #el.
$("#el").spin("large", "white"); // Produces a 'large' Spinner in white (or any valid CSS color).
$("#el").spin({ ... }); // Produces a Spinner using your custom settings.
 
$("#el").spin(false); // Kills the spinner.
*/

(function($) {
    var queue = [];
    var queueRunning = false;
    var presets = {
        "tiny": { lines: 8, length: 2, width: 2, radius: 3 },
        "small": { lines: 8, length: 4, width: 3, radius: 5 },
        "large": { lines: 10, length: 8, width: 4, radius: 8 }
    };

    $.fn.spin = function(opts, color) {
        queue.push({ self: this, opts: opts, color: color });
        runQueue();
        return this;
    };

    function runQueue() {
        if (queueRunning)
            return;
        queueRunning = true;
        require(['spin'], function (Spinner) {
            while (queue.length > 0) {
                var _params = queue.splice(0, 1);
                doit(Spinner, _params[0]);
            }
            queueRunning = false; 
        });
    }

    function doit(Spinner, params) {
        var self = params.self, opts = params.opts, color = params.color;
        if (typeof opts === "string") {
            if (opts in presets) {
                opts = presets[opts];
            } else {
                opts = {};
            }
            if (color) {
                opts.color = color;
            }
        }
        self.each(function() {
            var $this = $(this);
            data = $this.data();
            if (data.spinner) {
                data.spinner.stop();
                delete data.spinner;
            }
            if (opts !== false) {
                data.spinner = new Spinner($.extend({color: $this.css('color')}, opts)).spin(this);
            }
        });
    }
})(jQuery);
