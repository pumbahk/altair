package views;

class Workspace {
    public var components(get_components, null):Iterable<Component>;
    public var selection(get_selection, null):Array<Component>;
    public var numOfSelections(get_numOfSelections, null):Int;
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

    private function get_numOfSelections():Int {
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
        components_.add(component);
        component.workspace = this;
    }

    public function remove(component:Component) {
        component.workspace = null;
        components_.remove(component);
    }

    public function new() {
        components_ = new IdentifiableSet();
        selection_ = new IdentifiableSet();
    }
}
