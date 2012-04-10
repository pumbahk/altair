package views;

import js.JQuery;
import haxe.rtti.Meta;

private enum State {
    NONE;
    PRESSED(position:Point);
    DRAGGING(pof:Point);
}

class Component implements Identifiable {
    public var id(default, null):Int;
    public var renderer(default, null):Renderer;
    public var factory(default, null):ComponentFactory;
    public var workspace(default, set_workspace):Workspace;
    public var on(default, null):Dynamic;
    public var position(default, default):Point;
    public var size(default, default):Point;
    public var parent(default, null):Component;
    public var defaultCursor:MouseCursorKind;
    public var selected(default, null):Bool;
    var draggable:Bool;
    var state:State;
    var previousCursor:MouseCursorKind;
    var resizeBox:Renderer;

    function set_workspace(value:Workspace):Workspace {
        workspace = value;
        return value;
    }

    function initialize() {
        bindEvents();
    }

    function bindEvents() {
        var pressed = false;

        renderer.bind(EventKind.PRESS, function(e:Event) {
            state = PRESSED({
                x: (cast e).position.x - position.x,
                y: (cast e).position.y - position.y
            });
            on.press.call(this, e);
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

    public function select() {
        workspace.addToSelection(this, this);
    }

    public function unselect() {
        workspace.removeFromSelection(this, this);
    }

    public function hideResizeBox() {
        if (resizeBox == null)
            return;
        factory.stage.remove(cast resizeBox);
        resizeBox.dispose();
        resizeBox = null;
    }

    public function putResizeBox() {
        if (resizeBox != null)
            return;
        var resizeBox = factory.rendererFactory.create(cast Type.getClass(this), { variant: "resize_box" });
        factory.stage.add(cast resizeBox);
        resizeBox.bind(PRESS, function(e) {
            var corner = cast(e.extra, Direction);
            var startPosition = e.position;
            var initialPosition = position;
            var initialSize = size;
            resizeBox.bind(MOUSEMOVE, function(e) {
                switch (corner) {
                case NORTH_WEST:
                    position = {
                        x: initialPosition.x + (e.position.x - startPosition.x),
                        y: initialPosition.y + (e.position.y - startPosition.y)
                    };
                    size = {
                        x: initialSize.x - (e.position.x - startPosition.x),
                        y: initialSize.y - (e.position.y - startPosition.y),
                    };
                case NORTH_EAST:
                    position = {
                        x: initialPosition.x,
                        y: initialPosition.y + (e.position.y - startPosition.y)
                    };
                    size = {
                        x: initialSize.x + (e.position.x - startPosition.x),
                        y: initialSize.y - (e.position.y - startPosition.y),
                    };
                case SOUTH_WEST:
                    position = {
                        x: initialPosition.x + (e.position.x - startPosition.x),
                        y: initialPosition.y
                    };
                    size = {
                        x: initialSize.x - (e.position.x - startPosition.x),
                        y: initialSize.y + (e.position.y - startPosition.y),
                    };
                case SOUTH_EAST:
                    size = {
                        x: initialSize.x + (e.position.x - startPosition.x),
                        y: initialSize.y + (e.position.y - startPosition.y),
                    };
                default:
                }
                resizeBox.realize(this);
                renderer.realize(this);
            });
            resizeBox.bind(RELEASE, function(e) {
                resizeBox.releaseMouse();
                resizeBox.bind(MOUSEMOVE, null);
                resizeBox.bind(RELEASE, null);
            });
            resizeBox.captureMouse();
        });
        resizeBox.realize(this);
        this.resizeBox = resizeBox;
    }

    public function addedToSelection(cause:Dynamic) {
        selected = true;
        refresh();
        on.focused.call(this, { source:this, cause:cause });
    }

    public function removedFromSelection(cause:Dynamic) {
        selected = false;
        refresh();
        on.blur.call(this, { source:this, cause:cause });
    }

    public function refresh() {
        renderer.realize(this);
    }

    public function new(factory:ComponentFactory, id:Int, renderer:ComponentRenderer) {
        this.factory = factory;
        this.renderer = renderer;
        this.id = id;

        var meta = Meta.getType(Type.getClass(this));
        var on = { click: null, dragstart: null, dragend: null };
        var events = ["press", "click", "dragstart", "drag", "dragend", "focused", "blur"];
        if (meta.events != null)
            events.concat(meta.events);
        for (eventKind in events)
            Reflect.setField(on, eventKind, new EventListeners());
        this.on = on;
        this.draggable = true;
        this.state = NONE;
        this.parent = null;
        this.position = { x: 0., y: 0. };
        this.size = { x: 0., y: 0. };
        this.previousCursor = null;
        this.defaultCursor = MouseCursorKind.DEFAULT;
        this.resizeBox = null;

        initialize();
    }

}
