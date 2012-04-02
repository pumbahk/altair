interface Stage implements Disposable {
    public var view(default, null):View;
    public var size(get_size, null):Point;
    public var renderers(get_renderers, null):Iterable<ComponentRenderer>;
    public var cursor(default, set_cursor):MouseCursorKind;
    public function add(renderer:ComponentRenderer):Void;
    public function remove(renderer:ComponentRenderer):Void;
    public function dispose():Void;
}
