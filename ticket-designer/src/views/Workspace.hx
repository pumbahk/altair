package views;

@events("press", "release", "mouseout", "mousemove", "selectionchange")
class Workspace extends EventProducer {
    public var stage(default, null):Stage;
    public var components(get_components, null):Iterable<Component>;
    public var selection(get_selection, null):Array<Component>;
    public var selectionCount(get_selectionCount, null):Int;
    var components_:IdentifiableSet<Component>;
    var selection_:IdentifiableSet<Component>;

    private function get_components():Iterable<Component> {
        return components_;
    }

    private function get_selection():Array<Component> {
        var retval:Array<Component> = new Array();
        for (component in selection_)
            retval.push(component);
        return retval;
    }

    private function get_selectionCount():Int {
        return selection_.length;
    }

    public function addToSelection(component:Component, ?cause:Dynamic) {
        if (selection_.add(component)) {
            component.addedToSelection(cause);
        }
    }

    public function removeFromSelection(component:Component, ?cause:Dynamic) {
        if (selection_.remove(component)) {
            component.removedFromSelection(cause);
        }
    }

    public function clearSelection() {
        for (component in selection) { 
            removeFromSelection(component, this);
        }
    }

    public function add(component:Component) {
        component.on.press.do_(function(e:MouseEvent) {
            on.press.call(this, {
                position:e.position,
                screenPosition:e.screenPosition,
                left:e.left,
                middle:e.middle,
                right:e.right,
                extra:null,
                target:component
            });
        });
        component.on.mousemove.do_(function(e:MouseEvent) {
            on.mousemove.call(this, {
                position:e.position,
                screenPosition:e.screenPosition,
                left:e.left,
                middle:e.middle,
                right:e.right,
                extra:null,
                target:component
            });
        });
        component.on.mouseout.do_(function(e:MouseEvent) {
            on.mouseout.call(this, {
                position:e.position,
                screenPosition:e.screenPosition,
                left:e.left,
                middle:e.middle,
                right:e.right,
                extra:null,
                target:component
            });
        });
        component.on.release.do_(function(e:MouseEvent) {
            on.release.call(this, {
                position:e.position,
                screenPosition:e.screenPosition,
                left:e.left,
                middle:e.middle,
                right:e.right,
                extra:null,
                target:null
            });
        });
        components_.add(component);
        stage.add(cast component.renderer);
        component.workspace = this;
    }

    public function remove(component:Component) {
        component.unselect();
        component.workspace = null;
        components_.remove(component);
        stage.remove(cast(component.renderer, ComponentRenderer));
        component.renderer.dispose();
    }

    public function captureMouse() {
        stage.captureMouse();
    }

    public function releaseMouse() {
        stage.releaseMouse();
    }

    public function new(stage:Stage) {
        super();
        this.stage = stage;
        components_ = new IdentifiableSet();
        selection_ = new IdentifiableSet();

        stage.bind(EventKind.PRESS, function(e:MouseEvent) {
            on.press.call(this, {
                position:e.position,
                screenPosition:e.screenPosition,
                left:e.left,
                middle:e.middle,
                right:e.right,
                extra:null,
                target:null
            });
        });
        stage.bind(EventKind.MOUSEMOVE, function(e:MouseEvent) {
            on.mousemove.call(this, {
                position:e.position,
                screenPosition:e.screenPosition,
                left:e.left,
                middle:e.middle,
                right:e.right,
                extra:null,
                target:null
            });
        });
        stage.bind(EventKind.MOUSEOUT, function(e:MouseEvent) {
            on.mouseout.call(this, {
                position:e.position,
                screenPosition:e.screenPosition,
                left:e.left,
                middle:e.middle,
                right:e.right,
                extra:null,
                target:null
            });
        });
        stage.bind(EventKind.RELEASE, function(e:MouseEvent) {
            on.release.call(this, {
                position:e.position,
                screenPosition:e.screenPosition,
                left:e.left,
                middle:e.middle,
                right:e.right,
                extra:null,
                target:null
            });
        });
    }
}
