package views;

interface Renderer implements Disposable, implements MouseCapture, implements Identifiable {
    public var view(default, null):View;
    public var innerRenderSize(get_innerRenderSize, null):Point;
    public var outerRenderSize(get_outerRenderSize, null):Point;
    public function realize(component:Dynamic):Void;
    public function bind(event_kind:EventKind, handler:MouseEvent -> Void):Void;
}
