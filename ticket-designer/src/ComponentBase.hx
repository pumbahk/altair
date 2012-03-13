import js.JQuery;
import haxe.rtti.Meta;

private enum State {
    NONE;
    PRESSED(position:Point);
    DRAGGING(pof:Point);
}

class ComponentBase<Tself:Component> implements Component {
    public var renderer(default, null):Renderer;
    public var on(default, null):Dynamic;
    public var position(default, null):Point;
    public var parent(default, null):Component;
    public var defaultCursor:MouseCursorKind;
    private var draggable:Bool;
    private var state:State;
    var previousCursor:MouseCursorKind;

    public function new(renderer:ComponentRenderer) {
        var meta = Meta.getType(Type.getClass(this));
        var on = { click: null, dragstart: null, dragend: null };
        var events = ["click", "dragstart", "drag", "dragend"];
        if (meta.events != null)
            events.concat(meta.events);
        for (event_kind in events)
            untyped on[event_kind] = new EventListeners();
        this.on = on;
        this.draggable = true;
        this.state = NONE;
        this.parent = null;
        this.renderer = renderer;
        this.position = { x: 0., y: 0. };
        this.previousCursor = null;
        this.defaultCursor = MouseCursorKind.DEFAULT;

        bindEvents();
    }

    function bindEvents() {
        var pressed = false;

        renderer.bind(EventKind.PRESS, function(e:Event) {
            state = PRESSED({
                x: (cast e).position.x - position.x,
                y: (cast e).position.y - position.y
            });
            renderer.captureMouse();
        });
        renderer.bind(EventKind.MOUSEMOVE, function(e:Event) {
            var _renderer = cast(renderer, ComponentRenderer);
            if (previousCursor == null) {
                previousCursor = _renderer.stage.cursor;
                _renderer.stage.cursor = defaultCursor;
            }
            switch (state) {
            case PRESSED(pof):
                if (draggable) {
                    state = DRAGGING(pof);
                    this.position = {
                        x: (cast e).position.x - pof.x,
                        y: (cast e).position.y - pof.y
                    };
                    _renderer.opacity = .5;
                    on.dragstart.call(this, e);
                    this.refresh();
                }
            case DRAGGING(pof):
                this.position = {
                    x: (cast e).position.x - pof.x,
                    y: (cast e).position.y - pof.y
                };
                this.refresh();
                on.drag.call(this, e);
            default:
            }
        });

        renderer.bind(EventKind.MOUSEOUT, function(e:Event) {
            if (previousCursor != null) {
                cast(renderer, ComponentRenderer).stage.cursor = previousCursor;
                previousCursor = null;
            }
        });

        renderer.bind(EventKind.RELEASE, function(e:Event) {
            renderer.releaseMouse();
            switch (state) {
            case PRESSED(_):
                on.click.call(this, e);
            case DRAGGING(_):
                cast(this.renderer, ComponentRenderer).opacity = 1.;
                on.dragend.call(this, e);
                this.refresh();
            default:
            }
            state = NONE;
        });
    }

    public function refresh() {
        renderer.realize(this);
    }
}
