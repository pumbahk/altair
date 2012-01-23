interface Renderer implements Disposable {
    public var manager(default, set_manager):RenderingManager;
    public function setup():Void;
    public function dispose():Void;
    public function realize(component:Component):Void;
    public function bind(event_kind:EventKind, handler:Event -> Void):Void;
}
