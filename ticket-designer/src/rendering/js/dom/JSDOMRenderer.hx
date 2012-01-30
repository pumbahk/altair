package rendering.js.dom;
import js.JQuery;

class JSDOMRenderer implements Renderer {
    public var n(default, null):JQuery;
    public var id(default, null):Int;
    var manager_:JSDOMRenderingManager;
    public var manager(get_manager, null):RenderingManager;

    public var onPress:JqEvent->Void;
    public var onRelease:JqEvent->Void;
    public var onMouseMove:JqEvent->Void;

    var onPressHandler:Event->Void;
    var onReleaseHandler:Event->Void;
    var onMouseMoveHandler:Event->Void;

    public function setup(manager:RenderingManager, id:Int) {
        this.id = id;
        this.manager_ = cast(manager, JSDOMRenderingManager);
        if (n != null)
            n.appendTo(manager_.base);
    }

    public function dispose():Void {
        if (n != null)
            n.remove();
    }

    public function get_manager():RenderingManager {
        return manager_;
    }

    public function realize(component:Component):Void {}

    public function createMouseEvent(e:JqEvent):MouseEvent {
        return {
            source: this,
            cause: e,
            position:{ x:e.pageX - manager_.basePageOffset.x,
                       y:e.pageY - manager_.basePageOffset.y },
            left:(e.which & 1) != 0,
            middle:(e.which & 2) != 0,
            right:(e.which & 3) != 0 };
    }

    public function bind(event_kind:EventKind, handler:Event -> Void):Void {
        switch (event_kind) {
        case PRESS:
            if (onPressHandler == null)
                manager_.bindEvent(this, 'mousedown', onPress);
            else if (handler == null)
                manager_.unbindEvent(this, 'mousedown');
            onPressHandler = handler;
        case RELEASE:
            if (onReleaseHandler == null)
                manager_.bindEvent(this, 'mouseup', onRelease);
            else if (handler == null)
                manager_.unbindEvent(this, 'mouseup');
            onReleaseHandler = handler;
        case MOUSEMOVE:
            if (onMouseMoveHandler == null)
                manager_.bindEvent(this, 'mousemove', onMouseMove);
            else if (handler == null)
                manager_.unbindEvent(this, 'mousemove');
            onMouseMoveHandler = handler;
        }
    }

    public function captureMouse():Void {
        manager_.captureMouse(this);
    }

    public function releaseMouse():Void {
        manager_.releaseMouse(this);
    }

    public function new() {
        this.id = null;
        this.manager_ = null;
        var me = this;
        this.onPress = function (e:JqEvent):Void {
            me.onPressHandler(me.createMouseEvent(e));
        };

        this.onMouseMove = function(e:JqEvent):Void {
            me.onMouseMoveHandler(me.createMouseEvent(e));
        };

        this.onRelease = function(e:JqEvent):Void {
            me.onReleaseHandler(me.createMouseEvent(e));
        };
    }

}
