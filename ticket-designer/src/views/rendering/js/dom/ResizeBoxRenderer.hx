package views.rendering.js.dom;
import js.JQuery;
import js.JQuery.JqEvent;

class ResizeBoxRenderer extends JSDOMComponentRenderer {
    var position:Point;
    var size:Point;
    var cornerHandlers:Array<MouseEventsHandler>;
    static var corners = [
        [".nw", Direction.NORTH_WEST],
        [".sw", Direction.SOUTH_WEST],
        [".ne", Direction.NORTH_EAST],
        [".se", Direction.SOUTH_EAST]
    ];

    static function __init__() {
        Spi.rendererRegistry.addImplementation(Component, ResizeBoxRenderer, "resize_box");
    }

    public override function captureMouse():Void {
        view_.mouseEventsHandlerManager.captureMouse(cornerHandlers[Type.enumIndex(Direction.NORTH_WEST)]);
    }

    public override function releaseMouse():Void {
        view_.mouseEventsHandlerManager.releaseMouse(cornerHandlers[Type.enumIndex(Direction.NORTH_WEST)]);
    }

    public override function bind(eventKind:EventKind, handler:MouseEvent -> Void):Void {
        var existingHandler = handlers[Type.enumIndex(eventKind)];
        if (existingHandler == null) {
            if (handler != null) {
                for (pair in corners)
                    view_.mouseEventsHandlerManager.bindEvent(cornerHandlers[Type.enumIndex(pair[1])], eventKind);
            }
        } else {
            if (handler == null) {
                for (pair in corners)
                    view_.mouseEventsHandlerManager.unbindEvent(cornerHandlers[Type.enumIndex(pair[1])], eventKind);
            }
        }
        handlers[Type.enumIndex(eventKind)] = handler;
    }

    override function registerMouseEventsHandler() {
        for (pair in corners) {
            (function(part, partEnum) {
                cornerHandlers[Type.enumIndex(partEnum)] =
                    view_.mouseEventsHandlerManager.registerHandler(
                        new MouseEventsHandler(
                            n.find(part),
                            function(e) {
                                var handlerFunction = handlers[Type.enumIndex(EventKind.PRESS)];
                                if (handlerFunction != null)
                                    handlerFunction(createMouseEvent(e, partEnum));
                            },
                            function(e) {
                                var handlerFunction = handlers[Type.enumIndex(EventKind.RELEASE)];
                                if (handlerFunction != null)
                                    handlerFunction(createMouseEvent(e, partEnum));
                            },
                            function(e) {
                                var handlerFunction = handlers[Type.enumIndex(EventKind.MOUSEMOVE)];
                                if (handlerFunction != null)
                                    handlerFunction(createMouseEvent(e, partEnum));
                            },
                            function(e) {
                                var handlerFunction = handlers[Type.enumIndex(EventKind.MOUSEOUT)];
                                if (handlerFunction != null)
                                    handlerFunction(createMouseEvent(e, partEnum));
                            }
                        )
                    );
            })(pair[0], pair[1]);
        }
    }

    public override function setup():JQuery {
        var n = new JQuery('<div class="component-resize_box"><div class="corner nw"></div><div class="corner ne"></div><div class="corner sw"></div><div class="corner se"></div></div>'); 
        cornerHandlers = new Array();
        return n;
    }

    public override function realize(component:Dynamic):Void {
        position = component.position;
        size = component.size;
        view_.scheduleRefresh(this);
    }

    public override function refresh():Void {
        var position = view_.inchToPixelP(this.position);
        var size = view_.inchToPixelP(this.size);
        size.x -= Utils.toPixel(Utils.getComputedStyle(this.n[0], 'border-left-width'))
                + Utils.toPixel(Utils.getComputedStyle(this.n[0], 'border-right-width'));
        size.y -= Utils.toPixel(Utils.getComputedStyle(this.n[0], 'border-top-width'))
                + Utils.toPixel(Utils.getComputedStyle(this.n[0], 'border-bottom-width'));
        untyped __js__("this.n.css")(
            { left: Std.string(position.x) + "px",
              top: Std.string(position.y) + "px",
              width: Std.string(size.x) + "px",
              height: Std.string(size.y) + "px" });
        super.refresh();
    }
}
