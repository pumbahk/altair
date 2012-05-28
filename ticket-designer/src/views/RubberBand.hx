package views;

class RubberBand implements Renderable {
    public var renderer(default, null):Renderer;
    public var on(default, null):Dynamic;
    public var position(default, default):Point;
    public var size(default, default):Point;
    public var initialPosition(default, default):Point;
    
    public function refresh():Void {
        renderer.realize(this);
    }

    function bindEvents() {
        renderer.bind(EventKind.MOUSEMOVE, function(e:MouseEvent) {
            size = {
                x: Math.abs(e.position.x - initialPosition.x),
                y: Math.abs(e.position.y - initialPosition.y)
            };
            position = {
                x: e.position.x >= initialPosition.x ?
                    initialPosition.x: e.position.x,
                y: e.position.y >= initialPosition.y ?
                    initialPosition.y: e.position.y
            };
            refresh();
            on.mousemove.call(this, e);
        });
        renderer.bind(EventKind.RELEASE, function (e:Event) {
            on.release.call(this, e);
        });
    }

    public function new(renderer:Renderer) {
        this.renderer = renderer;
        var events = ["mousemove", "release"];
        on = {};
        for (event_kind in events)
            untyped on[event_kind] = new EventListeners();
        this.position = this.size = { x:0., y:0. };
        bindEvents();
    }
}
