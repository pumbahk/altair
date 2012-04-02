package views.rendering.js.dom;

import js.JQuery;

class JSDOMRenderer implements Renderer, implements MouseEventsHandler {
    public var id(default, null):Int;
    public var n(default, null):JQuery;
    public var view(default, null):View;
    public var innerRenderSize(get_innerRenderSize, null):Point;
    public var outerRenderSize(get_outerRenderSize, null):Point;

    public var onPress:JqEvent->Void;
    public var onRelease:JqEvent->Void;
    public var onMouseMove:JqEvent->Void;
    public var onMouseOut:JqEvent->Void;

    var view_:JSDOMView;

    var onPressHandler:Event->Void;
    var onReleaseHandler:Event->Void;
    var onMouseMoveHandler:Event->Void;
    var onMouseOutHandler:Event->Void;

    var innerRenderSize_:Point;
    var outerRenderSize_:Point;

    function get_innerRenderSize():Point {
        return innerRenderSize_;
    }

    function get_outerRenderSize():Point {
        return outerRenderSize_;
    }

    public function setup():JQuery {
        view_ = cast(view, JSDOMView);
        view_.addRenderer(this);
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

    public function refresh():Void {
        innerRenderSize_ = view_.pixelToInchP({ x:(0. + n.innerWidth()),
                                                y:(0. + n.innerHeight()) });
        outerRenderSize_ = view_.pixelToInchP({ x:(0. + n.outerWidth()),
                                                y:(0. + n.outerHeight()) });
    }

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

    public function new(id:Int, view:View) {
        this.id = id;
        this.view = view;
        this.n = setup();

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

    public function toString() {
        return Type.getClassName(Type.getClass(this)) + "{ id: " + id + " }";
    }
}
