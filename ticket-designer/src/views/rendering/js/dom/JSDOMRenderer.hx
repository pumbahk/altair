package views.rendering.js.dom;

import js.JQuery;

class JSDOMRenderer implements Renderer {
    public var id(default, null):Int;
    public var n(default, null):JQuery;
    public var view(default, null):View;
    public var innerRenderSize(get_innerRenderSize, null):Point;
    public var outerRenderSize(get_outerRenderSize, null):Point;

    var mouseEventsHandler:MouseEventsHandler;

    var view_:JSDOMView;

    var handlers:Array<MouseEvent->Void>;

    var innerRenderSize_:Point;
    var outerRenderSize_:Point;

    function get_innerRenderSize():Point {
        return innerRenderSize_;
    }

    function get_outerRenderSize():Point {
        return outerRenderSize_;
    }

    public function setup():JQuery {
        return null;
    }

    public function dispose():Void {
        releaseMouse();
        bind(PRESS, null);
        bind(RELEASE, null);
        bind(MOUSEMOVE, null);
        bind(MOUSEOUT, null);
        if (n != null)
            n.remove();
    }

    public function captureMouse():Void {
        if (mouseEventsHandler != null)
            view_.mouseEventsHandlerManager.captureMouse(mouseEventsHandler);
    }

    public function releaseMouse():Void {
        if (mouseEventsHandler != null)
            view_.mouseEventsHandlerManager.releaseMouse(mouseEventsHandler);
    }

    public function realize(renderable:Dynamic):Void {}

    public function refresh():Void {
        innerRenderSize_ = view_.pixelToInchP({ x:(0. + n.innerWidth()),
                                                y:(0. + n.innerHeight()) });
        outerRenderSize_ = view_.pixelToInchP({ x:(0. + n.outerWidth()),
                                                y:(0. + n.outerHeight()) });
    }

    function createMouseEvent(e:JqEvent, ?extra:Dynamic):MouseEvent {
        return null;
    }

    public function bind(eventKind:EventKind, handler:MouseEvent -> Void):Void {
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

    function registerMouseEventsHandler() {
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
    }

    public function new(id:Int, view:View) {
        this.id = id;
        this.view = view;
        this.view_ = cast(view, JSDOMView);
        this.handlers = [ null, null, null, null ];
        this.n = setup();

        this.view_.addRenderer(this);
        registerMouseEventsHandler();
    }

    public function toString() {
        return Type.getClassName(Type.getClass(this)) + "{ id: " + id + " }";
    }
}
