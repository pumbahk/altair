package views;

import js.JQuery;
import haxe.rtti.Meta;

@events("press", "release", "mouseout", "mousemove", "focus", "blur")
class Component extends EventProducer, implements Identifiable {
    public var id(default, null):Int;
    public var renderer(default, null):Renderer;
    public var workspace(default, set_workspace):Workspace;
    public var position(default, default):Point;
    public var size(default, default):Point;
    public var parent(default, null):Component;
    public var defaultCursor:MouseCursorKind;
    public var selected(default, null):Bool;
    public var draggable:Bool;
    var previousCursor:MouseCursorKind;

    function set_workspace(value:Workspace):Workspace {
        workspace = value;
        return value;
    }

    function initialize() {
    }

    public function select() {
        workspace.addToSelection(this, this);
    }

    public function unselect() {
        workspace.removeFromSelection(this, this);
    }

    public function addedToSelection(cause:Dynamic) {
        selected = true;
        refresh();
        on.focus.call(this, { source:this, cause:cause });
    }

    public function removedFromSelection(cause:Dynamic) {
        selected = false;
        refresh();
        on.blur.call(this, { source:this, cause:cause });
    }

    public function refresh() {
        renderer.realize(this);
    }

    public function new(id:Int, renderer:ComponentRenderer) {
        super();
        this.id = id;
        this.renderer = renderer;
        this.draggable = true;
        this.parent = null;
        this.position = { x: 0., y: 0. };
        this.size = { x: 0., y: 0. };
        this.previousCursor = null;
        this.defaultCursor = MouseCursorKind.DEFAULT;

        renderer.bind(EventKind.PRESS, function(e:Event) {
            on.press.call(this, e);
        });
        renderer.bind(EventKind.MOUSEMOVE, function(e:Event) {
            var _renderer = cast(renderer, ComponentRenderer);
            if (previousCursor == null) {
                previousCursor = _renderer.stage.cursor;
                _renderer.stage.cursor = defaultCursor;
            }
            on.mousemove.call(this, e);
        });

        renderer.bind(EventKind.MOUSEOUT, function(e:Event) {
            if (previousCursor != null) {
                cast(renderer, ComponentRenderer).stage.cursor = previousCursor;
                previousCursor = null;
            }
            on.mouseout.call(this, e);
        });

        renderer.bind(EventKind.RELEASE, function(e:Event) {
            on.release.call(this, e);
        });

        this.initialize();
    }
}
