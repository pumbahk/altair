package rendering.js.dom;

import js.JQuery;

class JSDOMRenderingManager extends BasicRenderingManagerImpl {
    public var basePageOffset(default, null):Point;
    public var base(default, set_base):JQuery;

    function set_base(value:JQuery):JQuery {
        base = value;
        if (base != null) {
            var offset = base.offset();
            basePageOffset = { x:offset.left, y:offset.top };
        }
        return base;
    }

    public function new(?base:JQuery) {
        super();
        this.base = base;
    }
}
