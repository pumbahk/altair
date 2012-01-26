interface Renderer implements Disposable {
    public var id(default, null):Int;
    public var manager(get_manager, null):RenderingManager;
    public function setup(manager:RenderingManager, id:Int):Void;
    public function dispose():Void;
    public function realize(component:Component):Void;
    public function bind(event_kind:EventKind, handler:Event -> Void):Void;
    public function captureMouse():Void;
    public function releaseMouse():Void;
}
