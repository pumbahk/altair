package rendering.js.dom;

import js.JQuery;

class JSDOMViewport implements Viewport {
    public var view(get_view, null):View;
    public var on(default, null): Dynamic;
    public var scrollPosition(get_scrollPosition, set_scrollPosition):Point;
    public var size(get_size, null):Point;
    public var n(default, set_n):JQuery;

    private var view_:JSDOMView;
    private var onScroll:JqEvent -> Void;

    public function set_n(value:JQuery):JQuery {
        if (n != null)
            n.unbind('scroll', onScroll);
        n = value;
        if (n != null) {
            refresh();
            n.bind('scroll', onScroll);
        }
        return value;
    }

    private function get_view():View {
        return view_;
    }

    private function get_scrollPosition():Point {
        return scrollPosition;
    }

    private function set_scrollPosition(value:Point):Point {
        scrollPosition = value;
        var positionInPixel = view_.inchToPixelP(value);
        n[0].scrollLeft = cast positionInPixel.x;
        n[0].scrollTop = cast positionInPixel.y;
        return value;
    }

    private function get_size():Point {
        return { x:0. + this.n.innerWidth(), y:0. + this.n.innerHeight() };
    }

    public function refresh():Void {
        scrollPosition = view_.pixelToInchP({ x:0. + n[0].scrollLeft, y:0. + n[0].scrollTop });
    }

    public function dispose() {
        if (n != null)
            n.unbind('scroll', onScroll);
    }

    public function new(view:JSDOMView) {
        this.view_ = view;
        this.on = { scroll: new EventListeners() };
        this.n = null;
        this.onScroll = function(e:JqEvent) {
            refresh();
            on.scroll.call(this, { source:this, cause: null, position: scrollPosition });
        };
    }
}
