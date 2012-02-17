package rendering.js.dom;

import js.JQuery;

class JSDOMStage extends BasicStageImpl<JSDOMComponentRenderer, JSDOMView> {
    public var base(default, set_base):JQuery;
    public var basePageOffset(default, null):Point;

    private function set_base(value:JQuery):JQuery {
        base = value;
        var offset = base.offset();
        basePageOffset = {
            x:cast(offset.left, Float),
            y:cast(offset.top, Float)
        };
        return value;
    }

    public function new(view:JSDOMView) {
        super(view);
    }
}
