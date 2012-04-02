package views.rendering.js.dom;

import js.JQuery;

class JSDOMStage extends BasicStageImpl<JSDOMComponentRenderer>, implements MouseEventsHandler {
    public var id(default, null):Int;
    public var n(default, set_n):JQuery;
    public var basePageOffset(default, null):Point;
    public var virtualSize:Point;

    public var onPress:JqEvent->Void;
    public var onRelease:JqEvent->Void;
    public var onMouseMove:JqEvent->Void;
    public var onMouseOut:JqEvent->Void;

    var onPressHandler:Event->Void;
    var onReleaseHandler:Event->Void;
    var onMouseMoveHandler:Event->Void;
    var onMouseOutHandler:Event->Void;

    public function refresh():Void {
        var actualSizeInPixel = cast(view, JSDOMView).inchToPixelP(virtualSize);
        recalculateBasePageOffset();
        untyped __js__("this.n.css")(
            { width: Std.string(actualSizeInPixel.x) + "px",
              height: Std.string(actualSizeInPixel.y) + "px" });
    }

    private function set_n(value:JQuery):JQuery {
        n = value;
        recalculateBasePageOffset();
        virtualSize = cast(view, JSDOMView).pixelToInchP({ x:0. + n.innerWidth(), y:0. + n.innerHeight() });
        return value;
    }

    public function recalculateBasePageOffset():Void {
        var offset = n.offset();
        basePageOffset = { x:0. + offset.left, y:0. + offset.top };
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
        cast(view, JSDOMView).captureMouse(this);
    }

    public override function releaseMouse():Void {
        cast(view, JSDOMView).releaseMouse();
    }

    public override function bind(event_kind:EventKind, handler:Event -> Void):Void {
        var view_ = cast(view, JSDOMView);
        switch (event_kind) {
        case PRESS:
            if (onPressHandler == null) {
                view_.bindEvent(this, 'mousedown', onPress);
            } else {
                if (handler != null)
                    throw new IllegalStateException("event is already bound");
                view_.unbindEvent(this, 'mousedown');
            }
            onPressHandler = handler;
        case RELEASE:
            if (onReleaseHandler == null) {
                view_.bindEvent(this, 'mouseup', onRelease);
            } else {
                if (handler != null)
                    throw new IllegalStateException("event is already bound");
                view_.unbindEvent(this, 'mouseup');
            }
            onReleaseHandler = handler;
        case MOUSEMOVE:
            if (onMouseMoveHandler == null) {
                view_.bindEvent(this, 'mousemove', onMouseMove);
            } else {
                if (handler != null)
                    throw new IllegalStateException("event is already bound");
                view_.unbindEvent(this, 'mousemove');
            }
            onMouseMoveHandler = handler;
        case MOUSEOUT:
            if (onMouseOutHandler == null) {
                view_.bindEvent(this, 'mouseout', onMouseOut);
            } else {
                if (handler != null)
                    throw new IllegalStateException("event is already bound");
                view_.unbindEvent(this, 'mouseout');
            }
            onMouseOutHandler = handler;
        }
    }

    function createMouseEvent(e:JqEvent):MouseEvent {
        return {
            source: this,
            cause: e,
            position: cast(view).pixelToInchP(
                { x: cast(e.pageX, Float) - basePageOffset.x,
                  y: cast(e.pageY, Float) - basePageOffset.y }),
            screenPosition: { x: 0. + e.pageX,  y: 0. + e.pageY },
            left: (e.which & 1) != 0,
            middle: (e.which & 2) != 0,
            right: (e.which & 3) != 0 };
    }

    public function new(view:View) {
        super(view);
        id = -1;

        this.onPressHandler = null;
        this.onReleaseHandler = null;
        this.onMouseMoveHandler = null;
        this.onMouseOutHandler = null;

        var me = this;
        this.onPress = function (e:JqEvent):Void {
            if (me.onPressHandler != null)
                me.onPressHandler(me.createMouseEvent(e));
        };

        this.onMouseMove = function(e:JqEvent):Void {
            if (me.onMouseMoveHandler != null)
                me.onMouseMoveHandler(me.createMouseEvent(e));
        };

        this.onMouseOut = function(e:JqEvent):Void {
            if (me.onMouseOutHandler != null)
                me.onMouseOutHandler(me.createMouseEvent(e));
        };

        this.onRelease = function(e:JqEvent):Void {
            if (me.onReleaseHandler != null)
                me.onReleaseHandler(me.createMouseEvent(e));
        };
    }
}
