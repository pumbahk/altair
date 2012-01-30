package rendering.js.dom;

import js.JQuery;
import js.Lib;

class JSDOMRenderingManager extends BasicRenderingManagerImpl<JSDOMRenderer> {
    public var basePageOffset(default, null):Point;
    public var base(default, set_base):JQuery;

    private var capturingRenderer:JSDOMRenderer;
    private var refreshQueue:Array<Void->Void>;

    private var eventHandlerHash:Hash<JqEvent->Void>;

    function set_base(value:JQuery):JQuery {
        base = value;
        if (base != null) {
            if (capturingRenderer != null)
                releaseMouse(capturingRenderer);
            var offset = base.offset();
            basePageOffset = { x:offset.left, y:offset.top };
        }
        return base;
    }

    public function scheduleRefresh(what:Void->Void) {
        refreshQueue.push(what);
    }

    public function refresh() {
        var refreshQueue = this.refreshQueue;
        this.refreshQueue = new Array();
        for (what in refreshQueue)
            what();
    }

    public function captureMouse(renderer:Renderer):Void {
        if (capturingRenderer != null)
            throw new IllegalStateException("mouse has already been captured by " + capturingRenderer);
        capturingRenderer = cast(renderer, JSDOMRenderer);
        new JQuery(Lib.document).bind('mousedown', capturingRenderer.onPress);
        new JQuery(Lib.document).bind('mouseup', capturingRenderer.onRelease);
        new JQuery(Lib.document).bind('mousemove', capturingRenderer.onMouseMove);
    }

    public function releaseMouse(renderer:Renderer):Void {
        if (capturingRenderer == null)
            throw new IllegalStateException("mouse is not captured");
        new JQuery(Lib.document).unbind('mousedown', capturingRenderer.onPress);
        new JQuery(Lib.document).unbind('mouseup', capturingRenderer.onRelease);
        new JQuery(Lib.document).unbind('mousemove', capturingRenderer.onMouseMove);
        capturingRenderer = null;
    }

    private static function buildEventHandlerKey(renderer:JSDOMRenderer, eventName:String):String {
        return Std.string(renderer.id) + ":" + eventName;
    }

    public function bindEvent(renderer:JSDOMRenderer, eventName:String, handler:JqEvent->Void) {
        var key = buildEventHandlerKey(renderer, eventName);
        if (eventHandlerHash.get(key) != null)
            throw new IllegalStateException("event " + eventName + " is already bound");

        var lambda = function(e:JqEvent) {
            if (capturingRenderer == null
                    || capturingRenderer.n[0] == e.target) {
                handler(e);
            }
        };
        eventHandlerHash.set(key, lambda);
        untyped __js__("renderer.n.bind")(eventName, lambda);
    }

    public function unbindEvent(renderer:JSDOMRenderer, eventName:String) {
        var key = buildEventHandlerKey(renderer, eventName);
        var handler = eventHandlerHash.get(key);
        if (handler == null)
            throw new IllegalStateException("event " + eventName + " is not bound yet");
        renderer.n.unbind(eventName, handler);
        eventHandlerHash.remove(key);
    }

    public function new(?base:JQuery) {
        super();
        this.base = base;
        this.capturingRenderer = null;
        this.refreshQueue = new Array();
        this.eventHandlerHash = new Hash();
    }
}
