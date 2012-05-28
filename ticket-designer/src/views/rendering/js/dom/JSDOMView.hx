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

    public var mouseEventsHandlerManager(default, null):MouseEventsHandlerManager;

    var refreshQueue:Hash<Int>;
    var batchRefreshNestCount:Int;
    var renderers:Hash<JSDOMRenderer>;

    private function set_ppi(value:Int):Int {
        ppi = value;
        refresh();
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
        refresh();
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

    public function removeRenderer(renderer:JSDOMRenderer) {
        renderers.remove(Std.string(renderer.id));
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

    public function refresh() {
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
        refreshQueue = new Hash();
        renderers = new Hash();
        mouseEventsHandlerManager = new MouseEventsHandlerManager();

        ppi = 114;
        zoom = 1.;

        viewport_ = new JSDOMViewport(this);
        viewport_.n = viewport;
        stage_ = new JSDOMStage(this);
        stage_.n = base;

        refresh();
    }
}
