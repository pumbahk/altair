interface Stage implements Disposable {
    public var view(get_view, null):View;
    public var renderers(get_renderers, null):Iterable<ComponentRenderer>;
    public function add(renderer:ComponentRenderer):Void;
    public function remove(renderer:ComponentRenderer):Void;
    public function dispose():Void;
}
