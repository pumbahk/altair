interface Renderer<Tcomponent:Component> {
    public function setup():Void;
    public function dispose():Void;
    public function realize(component:Tcomponent):Void;
    public function bind(event_kind:EventKind, handler:Event -> Void):Void;
}
