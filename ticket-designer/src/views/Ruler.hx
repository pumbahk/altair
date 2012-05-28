package views;

private enum State {
    NONE;
    PRESSED(position:Point);
    DRAGGING(pof:Point);
}

class Ruler implements Renderable {
    public var renderer(default, null):Renderer;
    public var on(default, null):Dynamic;
    public var offset:Int;
    public var unit:UnitKind;
    public var minimumGraduationWidthInPixel:Float;
    public var graduations:Array<Float>;
    private var state:State;

    public function refresh():Void {
        renderer.realize(this);
    }

    public function new(renderer:Renderer) {
        this.renderer = renderer;
        unit = MILLIMETER;
        minimumGraduationWidthInPixel = 4;
        graduations = [ 1., 5., 10., 25., 50., 100., 250., 500., 1000., ];

        var events = ["click", "dragstart", "drag", "dragend"];
        on = {};
        for (event_kind in events)
            untyped on[event_kind] = new EventListeners();
        this.state = NONE;
        bindEvents();
    }

    function bindEvents() {
        var pressed = false;

        renderer.bind(EventKind.PRESS, function(e:Event) {
            state = PRESSED({
                x: (cast e).position.x,
                y: (cast e).position.y
            });
        });
        renderer.bind(EventKind.MOUSEMOVE, function(e:Event) {
            switch (state) {
            case PRESSED(pof):
                state = DRAGGING(pof);
                renderer.captureMouse();
                on.dragstart.call(this, e);
            case DRAGGING(pof):
                on.drag.call(this, e);
            default:
            }
        });

        renderer.bind(EventKind.RELEASE, function(e:Event) {
            switch (state) {
            case PRESSED(_):
                on.click.call(this, e);
            case DRAGGING(_):
                renderer.releaseMouse();
                on.dragend.call(this, e);
            default:
            }
            state = NONE;
        });
    }
}
