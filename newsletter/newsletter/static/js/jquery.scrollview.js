/**
 * ScrollView - jQuery plugin 0.1
 *
 * This plugin supplies contents view by grab and drag scroll.
 *
 * Copyright (c) 2009 Toshimitsu Takahashi
 *
 * Released under the MIT license.
 *
 * == Usage =======================
 *   // apply to block element.
 *   $("#map").scrollview();
 *   
 *   // with setting grab and drag icon urls.
 *   //   grab: the cursor when mouse button is up.
 *   //   grabbing: the cursor when mouse button is down.
 *   //
 *   $("#map".scrollview({
 *     grab : "images/openhand.cur",
 *     grabbing : "images/closedhand.cur"
 *   });
 * ================================
 */
(function() {
    function ScrollView() { this.initialize.apply(this, arguments) }
    ScrollView.prototype = {
        initialize: function(container, config){
            // setting cursor.
            var mac = navigator.userAgent.indexOf("Mac OS") != -1;
            if ($.browser.opera) {
                this.grab = "default";
                this.grabbing = "move";
            } else if (!(mac && $.browser.mozilla) && config) {
                if (config.grab) {
                    this.grab = "url(\"" + config.grab + "\"),default";
                }
                if (config.grabbing) {
                    this.grabbing = "url(" + config.grabbing + "),move";
                }
            } else if ($.browser.mozilla) {
                this.grab = "-moz-grab";
                this.grabbing = "-moz-grabbing";
            } else {
                this.grab = "default";
                this.grabbing = "move";
            }
            
            // Get container and image.
            this.m = $(container).css("position", "relative");
            this.i = this.m.children().css({cursor: this.grab, zIndex: 0 });
            this.offsetParent = $(this.i[0].parentNode).offsetParent()[0];

            this.isgrabbing = false;
            this.isselecting = false;
            this.selectbox = null;

            this.mode = 'scroll';

            // Set mouse events.
            var self = this;
            this.i.mousedown(function(e){
                self.xp = e.pageX;
                self.yp = e.pageY;
                if (self.mode == 'scroll') {
                    self.startgrab();
                } else if (self.mode == 'select') {
                    self.startselect();
                }
                return false;
            }).mousemove(function(e){
                if (self.isgrabbing) {
                    self.scrollTo(self.xp - e.pageX, self.yp - e.pageY);
                    self.xp = e.pageX;
                    self.yp = e.pageY;
                } else if (self.isselecting) {
                    self.resizeselectbox(e);
                }
                return false;
            })
            .mouseout(function(){
                if (self.mode == 'scroll') {
                    self.stopgrab();
                }
            })
            .mouseup(function(e){
                if (self.mode == 'scroll') {
                    self.stopgrab();
                } else {
                    self.stopselect(e);
                }
            })
            .dblclick(function(){
                if (self.mode == 'scroll') {
                    var _m = self.m;
                    var off = _m.offset();
                    var dx = self.xp - off.left - _m.width() / 2;
                    if (dx < 0) {
                        dx = "+=" + dx + "px";
                    } else {
                        dx = "-=" + -dx + "px";
                    }
                    var dy = self.yp - off.top - _m.height() / 2;
                    if (dy < 0) {
                        dy = "+=" + dy + "px";
                    } else {
                        dy = "-=" + -dy + "px";
                    }
                    _m.animate({ scrollLeft:  dx, scrollTop: dy },
                               "normal", "swing");
                }
            });
            this.i.find('img').load(function() {
                self.i.css({ width: this.width + "px", height: this.height + "px" });
                self.centering();
            });
        },
        centering: function(){
            var _m = this.m;
            var w = this.i.width() - _m.width();
            var h = this.i.height() - _m.height();
            _m.scrollLeft(w / 2).scrollTop(h / 2);
        },
        startgrab: function(){
            this.isgrabbing = true;
            this.i.css("cursor", this.grabbing);
        },
        stopgrab: function(){
            this.isgrabbing = false;
            this.i.css("cursor", this.grab);
        },
        scrollTo: function(dx, dy){
            var _m = this.m;
            var x = _m.scrollLeft() + dx;
            var y = _m.scrollTop() + dy;
            _m.scrollLeft(x).scrollTop(y);
        },
        startselect: function(){
            this.isselecting = true;
            var self = this;
            this.selectbox = $("<div></div>").css({
                position: "absolute",
                left: '0px',
                top: '0px',
                width: '0px',
                height: '0px',
                border: '1px dotted #000',
                backgroundColor: 'rgba(0, 0, 128, .25)',
                zIndex: 2
            })
            .mousemove(function(e) { self.resizeselectbox(e) })
            .mouseup(function(e) { self.stopselect(e); });
            this.m.prepend(this.selectbox);
        },
        stopselect: function(){
            this.selectbox.remove();
            this.isselecting = false;
            this.m.trigger("selectionadded");
        },
        pageOffset: function() {
            var n = this.i[0];
            var offsetLeft = this.offsetParent.offsetLeft + n.parentNode.offsetLeft;
            var offsetTop = this.offsetParent.offsetTop + n.parentNode.offsetTop;

            return { x: offsetLeft - n.parentNode.scrollLeft,
                     y: offsetTop - n.parentNode.scrollTop }; 
        },
        resizeselectbox: function(e) {
            width = e.pageX - this.xp - 2;
            height = e.pageY - this.yp - 2;
            var offset = this.pageOffset();
            if (width >= 0) {
              left = this.xp - offset.x;
            } else {
              width = -width;
              left = e.pageX - offset.x;
            }
            if (height >= 0) {
              top = this.yp - offset.y;
            } else {
              height = -height;
              top = e.pageY - offset.y;
            }
            this.selectbox.css({
                left: left + "px",
                top: top + "px",
                width: width + "px",
                height: height + "px"
            });
        }
    };
      
    jQuery.fn.scrollview = function(config){
        return this.each(function(){
            $(this).data('scrollView', new ScrollView(this, config));
        });
    };
})(jQuery);
