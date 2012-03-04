interface Renderer implements Disposable {
    public var id(default, null):Int;
    public var view(default, null):View;
    public function dispose():Void;
    public function realize(component:Dynamic):Void;
    public function bind(event_kind:EventKind, handler:Event -> Void):Void;
    public function captureMouse():Void;
    public function releaseMouse():Void;
}
