package views.rendering.js.dom;

import js.JQuery;
import js.Lib;

class JSDOMView implements View {
    public var ppi(default, set_ppi):Int;
    public var zoom(default, set_zoom):Float;
    public var viewport(get_viewport, null):Viewport;
    public var stage(get_stage, null):Stage;

    public var viewport_:JSDOMViewport;
    public var stage_:JSDOMStage;

    var capturing:MouseEventsHandler;
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
        if (viewport_ != null) {
            var oldViewportSize = pixelToInchP(viewport_.size);
            var oldScrollPosition = viewport_.scrollPosition;
            var center:Point = {
                x:oldViewportSize.x / 2 + oldScrollPosition.x,
                y:oldViewportSize.y / 2 + oldScrollPosition.y };
            zoom = value;
            var newViewportSize = pixelToInchP(viewport_.size);
            var newScrollPosition:Point = {
                x:center.x - newViewportSize.x / 2,
                y:center.y - newViewportSize.y / 2 };
            viewport_.scrollPosition = newScrollPosition;
        } else {
            zoom = value;
        }
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
        if (viewport_ != null)
            viewport_.dispose();
        if (stage_ != null)
            stage_.dispose();
    }

    public function captureMouse(handlerObject:MouseEventsHandler):Void {
        if (capturing != null)
            throw new IllegalStateException("mouse has already been captured by " + capturing);
        capturing = handlerObject;
        if (capturing.onPress != null)
            new JQuery(Lib.document).bind('mousedown', capturing.onPress);
        if (capturing.onRelease != null)
            new JQuery(Lib.document).bind('mouseup', capturing.onRelease);
        if (capturing.onMouseMove != null)
            new JQuery(Lib.document).bind('mousemove', capturing.onMouseMove);
    }

    public function releaseMouse():Void {
        if (capturing == null)
            return;
        if (capturing.onPress != null)
            new JQuery(Lib.document).unbind('mousedown', capturing.onPress);
        if (capturing.onRelease != null)
            new JQuery(Lib.document).unbind('mouseup', capturing.onRelease);
        if (capturing.onMouseMove != null)
            new JQuery(Lib.document).unbind('mousemove', capturing.onMouseMove);
        capturing = null;
    }

    private static function buildEventHandlerKey(handlerObject:MouseEventsHandler, eventName:String):String {
        return Std.string(handlerObject.id) + ":" + eventName;
    }

    public function bindEvent(handlerObject:MouseEventsHandler, eventName:String, handler:JqEvent->Void) {
        var key = buildEventHandlerKey(handlerObject, eventName);
        if (eventHandlerHash.get(key) != null)
            throw new IllegalStateException("event " + eventName + " is already bound");

        var lambda = function(e:JqEvent) {
            if (capturing == null
                    || capturing.n[0] == e.target) {
                handler(e);
                return false;
            }
            return true;
        };
        eventHandlerHash.set(key, untyped lambda);
        handlerObject.n.bind(eventName, untyped lambda);
    }

    public function unbindEvent(handlerObject:MouseEventsHandler, eventName:String) {
        var key = buildEventHandlerKey(handlerObject, eventName);
        var handler = eventHandlerHash.get(key);
        if (handler == null)
            throw new IllegalStateException("event " + eventName + " is not bound yet");
        handlerObject.n.unbind(eventName, handler);
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
   
    public function anyToPixel(unit:UnitKind, value:Float):Float {
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

    public function anyToPixelP(unit:UnitKind, value:Point):Point {
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
        if (viewport_ != null)
            viewport_.refresh();
        if (stage_ != null)
            stage_.refresh();
        if (renderers != null) {
            if (batchRefreshNestCount == 0) {
                this.refreshQueue = new Hash();
                for (id in renderers.keys())
                    renderers.get(id).refresh();
            } else {
                for (id in renderers.keys())
                    refreshQueue.set(id, 1);
            }
        }
    }

    public function new(base:JQuery, viewport:JQuery) {
        batchRefreshNestCount = 0;
        capturing = null;
        eventHandlerHash = new Hash();
        refreshQueue = new Hash();
        renderers = new Hash();

        ppi = 114;
        zoom = 1.;

        viewport_ = new JSDOMViewport(this);
        viewport_.n = viewport;
        stage_ = new JSDOMStage(this);
        stage_.n = base;

        refreshAll();
    }
}
