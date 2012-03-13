package rendering.js.dom;

import js.JQuery;

class JSDOMRenderer implements Renderer {
    public var id(default, null):Int;
    public var n(default, null):JQuery;
    public var view(default, set_view):View;

    public var view_:JSDOMView;

    public var onPress:JqEvent->Void;
    public var onRelease:JqEvent->Void;
    public var onMouseMove:JqEvent->Void;
    public var onMouseOut:JqEvent->Void;

    var onPressHandler:Event->Void;
    var onReleaseHandler:Event->Void;
    var onMouseMoveHandler:Event->Void;
    var onMouseOutHandler:Event->Void;

    private function set_view(value:View):View {
        view_ = cast(value, JSDOMView);
        view_.addRenderer(this);
        return value;
    }

    public function setup():JQuery {
        return null;
    }

    public function dispose():Void {
        if (n != null)
            n.remove();
    }

    public function captureMouse():Void {
        view_.captureMouse(this);
    }

    public function releaseMouse():Void {
        view_.releaseMouse();
    }

    public function realize(renderable:Dynamic):Void {}

    public function refresh():Void {}

    function createMouseEvent(e:JqEvent):MouseEvent {
        return null;
    }

    public function bind(event_kind:EventKind, handler:Event -> Void):Void {
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

    public function new(id:Int) {
        this.id = id;
        this.n = setup();
        setup();

        this.onPressHandler = null;
        this.onReleaseHandler = null;
        this.onMouseMoveHandler = null;

        var me = this;
        this.onPress = function (e:JqEvent):Void {
            me.onPressHandler(me.createMouseEvent(e));
        };

        this.onMouseMove = function(e:JqEvent):Void {
            me.onMouseMoveHandler(me.createMouseEvent(e));
        };

        this.onMouseOut = function(e:JqEvent):Void {
            me.onMouseOutHandler(me.createMouseEvent(e));
        };

        this.onRelease = function(e:JqEvent):Void {
            me.onReleaseHandler(me.createMouseEvent(e));
        };
    }

    public function toString() {
        return Type.getClassName(Type.getClass(this)) + "{ id: " + id + " }";
    }
}
