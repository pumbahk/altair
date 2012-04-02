package rendering.js.dom;

import js.JQuery;

class JSDOMStage extends BasicStageImpl<JSDOMComponentRenderer> {
    public var base(default, set_base):JQuery;
    public var basePageOffset(default, null):Point;
    public var virtualSize:Point;

    public function refresh():Void {
        var actualSizeInPixel = cast(view, JSDOMView).inchToPixelP(virtualSize);
        untyped __js__("this.base.css")(
            { width: Std.string(actualSizeInPixel.x) + "px",
              height: Std.string(actualSizeInPixel.y) + "px" });
    }

    private function set_base(value:JQuery):JQuery {
        base = value;
        var offset = base.offset();
        basePageOffset = {
            x:cast(offset.left, Float),
            y:cast(offset.top, Float)
        };
        virtualSize = cast(view, JSDOMView).pixelToInchP({ x:0. + base.innerWidth(), y:0. + base.innerHeight() });
        return value;
    }

    override function get_size():Point {
        return virtualSize;
    }

    override function set_cursor(value:MouseCursorKind):MouseCursorKind {
        switch (value) {
        case DEFAULT:
            base.css('cursor', 'default');
        case POINTER:
            base.css('cursor', 'pointer');
        case CROSSHAIR:
            base.css('cursor', 'crosshair');
        case MOVE:
            base.css('cursor', 'move');
        }
        return super.set_cursor(value);
    }
}
