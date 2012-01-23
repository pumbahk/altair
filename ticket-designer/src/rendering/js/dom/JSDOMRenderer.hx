package rendering.js.dom;
import js.JQuery;

class JSDOMRenderer {
    public var n(default, null):JQuery;
    public var base(default, null):JQuery;
    public var manager(default, set_manager):RenderingManager;

    public function new(base:JQuery) {
        this.base = base;
        this.manager = null;
    }

    function set_manager(manager:RenderingManager):RenderingManager {
        return this.manager = manager;
    }

    public function dispose():Void {
        if (n != null)
            n.remove();
    }
}
