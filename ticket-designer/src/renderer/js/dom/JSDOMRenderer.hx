package renderer.js.dom;
import js.JQuery;

class JSDOMRenderer {
    public var n:JQuery;

    public function new() {
        n = null;
    }

    public function dispose():Void {
        if (n)
            n.remove();
    }
}
