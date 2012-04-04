package views;

class BasicStageImpl<Trenderer:ComponentRenderer> implements Stage {
    public var view(default, null):View;
    public var size(get_size, null):Point;
    public var renderers(get_renderers, null):Iterable<ComponentRenderer>;
    public var cursor(default, set_cursor):MouseCursorKind;
    public var screenOffset(default, null):Point;
    var renderers_:IdentifiableSet<Trenderer>;

    function set_cursor(value:MouseCursorKind):MouseCursorKind {
        cursor = value;
        return value;
    }

    public function add(renderer:ComponentRenderer):Void {
        renderers_.add(cast renderer);
        renderer.stage = this;
    }

    public function remove(renderer:ComponentRenderer):Void {
        renderer.stage = null;
        renderers_.remove(cast renderer);
    }

    public function dispose():Void {
        for (renderer in renderers_) {
            var throwables = new Array<Throwable>();
            try {
                renderer.dispose();
            } catch (e:Throwable) {
                throwables.push(e); 
            }
            if (throwables.length > 0)
                throw new Throwables(throwables);
        }
    }

    private function get_renderers():Iterable<ComponentRenderer> {
        return renderers_;
    }

    function get_size():Point {
        return null;
    }

    public function new(view:View) {
        this.renderers_ = new IdentifiableSet();
        this.view = view;
    }

    public function captureMouse():Void {}

    public function releaseMouse():Void {}

    public function bind(event_kind:EventKind, handler:Event -> Void):Void {}
}
