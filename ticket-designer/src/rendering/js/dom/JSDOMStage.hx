package rendering.js.dom;

import js.JQuery;

class JSDOMStage extends BasicStageImpl<JSDOMComponentRenderer, JSDOMView> {
    public var base(default, set_base):JQuery;
    public var basePageOffset(default, null):Point;

    public function refresh():Void {}

    private function set_base(value:JQuery):JQuery {
        base = value;
        var offset = base.offset();
        basePageOffset = {
            x:cast(offset.left, Float),
            y:cast(offset.top, Float)
        };
        return value;
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

    public function new(view:JSDOMView) {
        super(view);
    }
}
