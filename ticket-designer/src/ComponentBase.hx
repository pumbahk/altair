import js.JQuery;
import haxe.rtti.Meta;

private enum State {
    NONE;
    PRESSED(position:Point);
    DRAGGING;
}

class ComponentBase<Tself:Component> implements Component {
    public var renderer(default, set_renderer):Renderer;
    public var on(default, null):Dynamic;
    public var position(default, null):Point;
    public var parent(default, null):Component;
    private var draggable:Bool;
    private var state:State;

    public function new(?renderer:Renderer) {
        var meta = Meta.getType(Type.getClass(this));
        var on = { click: null, dragstart: null, dragend: null };
        var events = ["click", "dragstart", "dragend"];
        if (meta.events != null)
            events.concat(meta.events);
        for (event_kind in events)
            untyped on[event_kind] = new EventListeners();
        this.on = on;
        this.draggable = true;
        this.state = NONE;
        this.parent = null;
        this.renderer = renderer;
        this.position = { x: 0, y: 0 };

        bindEvents();
    }

    function bindEvents() {
        var pressed = false;

        renderer.bind(EventKind.PRESS, function(e:Event) {
            state = PRESSED((cast e).position);
        });

        renderer.bind(EventKind.MOUSEMOVE, function(e:Event) {
            switch (state) {
            case PRESSED(_):
                if (draggable) {
                    state = DRAGGING;
                    on.dragstart.call(this, e);
                }
            default:
            }
        });

        renderer.bind(EventKind.RELEASE, function(e:Event) {
            switch (state) {
            case PRESSED(_):
                on.click.call(this, e);
            case DRAGGING:
                on.dragend.call(this, e);
            default:
            }
            state = NONE;
        });
    }

    public function refresh() {
        renderer.realize(this);
    }

    private function set_renderer(renderer:Renderer):Renderer {
        return this.renderer = renderer; 
    }
}
