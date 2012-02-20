package rendering.js.dom;

import js.JQuery;
import js.Lib;

class JSDOMView implements View {
    public var ppi(default, set_ppi):Int;
    public var zoom(default, set_zoom):Float;
    public var viewport(get_viewport, null):Viewport;
    public var stage(get_stage, null):Stage;

    public var viewport_:JSDOMViewport;
    public var stage_:JSDOMStage;
    var capturingRenderer:JSDOMRenderer;
    var eventHandlerHash:Hash<JqEvent->Void>;
    var refreshQueue:Hash<Int>;
    var batchRefreshNestCount:Int;
    var renderers:Hash<JSDOMRenderer>;

    private function set_ppi(value:Int):Int {
        ppi = value;
        refreshAll();
        return value;
    }

    private function set_zoom(value:Float):Float {
        zoom = value;
        refreshAll();
        return value;
    }

    private function get_viewport():Viewport {
        return viewport_;
    }

    private function get_stage():Stage {
        return stage_;
    }

    public function dispose():Void {
        viewport_.dispose();
        stage_.dispose();
    }

    public function captureMouse(renderer:JSDOMRenderer):Void {
        if (capturingRenderer != null)
            throw new IllegalStateException("mouse has already been captured by " + capturingRenderer);
        capturingRenderer = cast(renderer, JSDOMRenderer);
        if (capturingRenderer.onPress != null)
            new JQuery(Lib.document).bind('mousedown', capturingRenderer.onPress);
        if (capturingRenderer.onRelease != null)
            new JQuery(Lib.document).bind('mouseup', capturingRenderer.onRelease);
        if (capturingRenderer.onMouseMove != null)
            new JQuery(Lib.document).bind('mousemove', capturingRenderer.onMouseMove);
    }

    public function releaseMouse():Void {
        if (capturingRenderer == null)
            return;
        if (capturingRenderer.onPress != null)
            new JQuery(Lib.document).unbind('mousedown', capturingRenderer.onPress);
        if (capturingRenderer.onRelease != null)
            new JQuery(Lib.document).unbind('mouseup', capturingRenderer.onRelease);
        if (capturingRenderer.onMouseMove != null)
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

    public function pixelToInch(value:Float):Float {
        return value / ppi / zoom;
    }

    public function pixelToInchP(value:Point):Point {
        return { x:value.x / ppi / zoom, y:value.y / ppi / zoom };
    }

    public function inchToPixel(value:Float):Float {
        return value * ppi * zoom;
    }

    public function inchToPixelP(value:Point):Point {
        return { x:value.x * ppi * zoom , y:value.y * ppi * zoom };
    }
   
    public function anyToPixel(unit:UnitKind, value:Float) {
        switch (unit) {
        case INCH:
            return inchToPixel(value);
        case POINT:
            return inchToPixel(UnitUtils.pointToInch(value));
        case PICA:
            return inchToPixel(UnitUtils.picaToInch(value));
        case MILLIMETER:
            return inchToPixel(UnitUtils.mmToInch(value));
        case CENTIMETER:
            return inchToPixel(UnitUtils.cmToInch(value));
        case METER:
            return inchToPixel(UnitUtils.meterToInch(value));
        case PIXEL:
            return value * zoom;
        }
    }

    public function anyToPixelP(unit:UnitKind, value:Point) {
        switch (unit) {
        case INCH:
            return inchToPixelP(value);
        case POINT:
            return inchToPixelP(UnitUtils.pointToInchP(value));
        case PICA:
            return inchToPixelP(UnitUtils.picaToInchP(value));
        case MILLIMETER:
            return inchToPixelP(UnitUtils.mmToInchP(value));
        case CENTIMETER:
            return inchToPixelP(UnitUtils.cmToInchP(value));
        case METER:
            return inchToPixelP(UnitUtils.meterToInchP(value));
        case PIXEL:
            return { x: value.x * zoom, y: value.y * zoom };
        }
    }

    public function addRenderer(renderer:JSDOMRenderer) {
        renderers.set(Std.string(renderer.id), renderer);
    }

    public function beginBatchRefresh() {
        batchRefreshNestCount++;
    }

    public function endBatchRefresh() {
        if (batchRefreshNestCount == 0)
            throw new IllegalStateException("endBatchRefresh() called prior to beginBatcnRefresh()");
        if (--batchRefreshNestCount == 0) {
            var refreshQueue = this.refreshQueue;
            this.refreshQueue = new Hash();
            for (id in refreshQueue.keys())
                renderers.get(id).refresh();
        }
    }

    public function scheduleRefresh(what:JSDOMRenderer) {
        if (batchRefreshNestCount == 0)
            what.refresh();
        else
            refreshQueue.set(Std.string(what.id), 1);
    }

    public function refreshAll() {
        if (batchRefreshNestCount == 0) {
            this.refreshQueue = new Hash();
            for (id in renderers.keys())
                renderers.get(id).refresh();
        } else {
            for (id in renderers.keys())
                refreshQueue.set(id, 1);
        }
    }

    public function new(base:JQuery, viewport:JQuery) {
        capturingRenderer = null;
        eventHandlerHash = new Hash();
        refreshQueue = new Hash();
        renderers = new Hash();
        batchRefreshNestCount = 0;
        ppi = 114;
        zoom = 1.;

        viewport_ = new JSDOMViewport(this);
        stage_ = new JSDOMStage(this);
        viewport_.n = viewport;
        stage_.base = base;
    }
}
