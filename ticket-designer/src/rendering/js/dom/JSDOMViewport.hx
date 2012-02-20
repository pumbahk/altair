package rendering.js.dom;

import js.JQuery;

class JSDOMViewport implements Viewport {
    public var view(get_view, null):View;
    public var on(default, null): Dynamic;
    public var n(default, set_n):JQuery;

    private var view_:JSDOMView;
    private var scrollPosition:Point;
    private var onScroll:JqEvent -> Void;

    public function set_n(value:JQuery):JQuery {
        if (n != null)
            n.unbind('scroll', onScroll);
        n = value;
        if (n != null) {
            scrollPosition = view_.pixelToInchP({ x:0. + n[0].scrollLeft, y:0. + n[0].scrollTop });
            n.bind('scroll', onScroll);
        }
        return value;
    }

    private function get_view():View {
        return view_;
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
            scrollPosition = view_.pixelToInchP({ x:0. + e.target.scrollLeft, y:0. + e.target.scrollTop });
            on.scroll.call(this, { source:this, cause: null, position: scrollPosition });
        };
    }
}
