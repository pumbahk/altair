interface Stage implements Disposable, implements MouseCapture {
    public var view(default, null):View;
    public var size(get_size, null):Point;
    public var renderers(get_renderers, null):Iterable<ComponentRenderer>;
    public var cursor(default, set_cursor):MouseCursorKind;
    public function add(renderer:ComponentRenderer):Void;
    public function remove(renderer:ComponentRenderer):Void;
    public function bind(event_kind:EventKind, handler:Event -> Void):Void;
}
