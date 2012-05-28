package views.rendering.js.dom;

import js.JQuery;

class JSDOMStage extends BasicStageImpl<JSDOMComponentRenderer> {
    public var n(default, set_n):JQuery;
    public var virtualSize:Point;

    var mouseEventsHandler:MouseEventsHandler;

    var handlers:Array<MouseEvent->Void>;

    public function refresh():Void {
        var actualSizeInPixel = cast(view, JSDOMView).inchToPixelP(virtualSize);
        recalculateBasePageOffset();
        untyped __js__("this.n.css")(
            { width: Std.string(actualSizeInPixel.x) + "px",
              height: Std.string(actualSizeInPixel.y) + "px" });
    }

    private function set_n(value:JQuery):JQuery {
        if (n != null)
            cast(view, JSDOMView).mouseEventsHandlerManager.unregisterHandler(mouseEventsHandler);

        n = value;
        recalculateBasePageOffset();
        virtualSize = cast(view, JSDOMView).pixelToInchP({ x:0. + n.innerWidth(), y:0. + n.innerHeight() });

        this.mouseEventsHandler = cast(view, JSDOMView).mouseEventsHandlerManager.registerHandler(new MouseEventsHandler(
            n,
            function (e:JqEvent):Void {
                var handlerFunction = handlers[Type.enumIndex(EventKind.PRESS)];
                if (handlerFunction != null)
                    handlerFunction(createMouseEvent(e));
            },
            function(e:JqEvent):Void {
                var handlerFunction = handlers[Type.enumIndex(EventKind.RELEASE)];
                if (handlerFunction != null)
                    handlerFunction(createMouseEvent(e));
            },
            function(e:JqEvent):Void {
                var handlerFunction = handlers[Type.enumIndex(EventKind.MOUSEMOVE)];
                if (handlerFunction != null)
                    handlerFunction(createMouseEvent(e));
            },
            function(e:JqEvent):Void {
                var handlerFunction = handlers[Type.enumIndex(EventKind.MOUSEOUT)];
                if (handlerFunction != null)
                    handlerFunction(createMouseEvent(e));
            }
        ));

        return value;
    }

    public function recalculateBasePageOffset():Void {
        var offset = n.offset();
        screenOffset = { x:0. + offset.left, y:0. + offset.top };
    }

    override function get_size():Point {
        return virtualSize;
    }

    override function set_cursor(value:MouseCursorKind):MouseCursorKind {
        switch (value) {
        case DEFAULT:
            n.css('cursor', 'default');
        case POINTER:
            n.css('cursor', 'pointer');
        case CROSSHAIR:
            n.css('cursor', 'crosshair');
        case MOVE:
            n.css('cursor', 'move');
        }
        return super.set_cursor(value);
    }

    public override function captureMouse():Void {
        cast(view, JSDOMView).mouseEventsHandlerManager.captureMouse(mouseEventsHandler);
    }

    public override function releaseMouse():Void {
        cast(view, JSDOMView).mouseEventsHandlerManager.releaseMouse(mouseEventsHandler);
    }

    public override function bind(eventKind:EventKind, handler:MouseEvent -> Void):Void {
        var view_ = cast(view, JSDOMView);
        var existingHandler = handlers[Type.enumIndex(eventKind)];
        if (existingHandler == null) {
            if (handler != null)
                view_.mouseEventsHandlerManager.bindEvent(mouseEventsHandler, eventKind);
        } else {
            if (handler == null)
                view_.mouseEventsHandlerManager.unbindEvent(mouseEventsHandler, eventKind);
        }
        handlers[Type.enumIndex(eventKind)] = handler;
    }

    function createMouseEvent(e:JqEvent, ?extra:Dynamic):MouseEvent {
        return {
            source: this,
            cause: e,
            position: cast(view).pixelToInchP(
                { x: cast(e.pageX, Float) - screenOffset.x,
                  y: cast(e.pageY, Float) - screenOffset.y }),
            screenPosition: { x: 0. + e.pageX,  y: 0. + e.pageY },
            left: (e.which & 1) != 0,
            middle: (e.which & 2) != 0,
            right: (e.which & 3) != 0,
            extra: extra
        };
    }

    public function toString():String {
        return "stage";
    }

    public function new(view:View) {
        super(view);
        this.handlers = [ null, null, null, null ];
    }
}
