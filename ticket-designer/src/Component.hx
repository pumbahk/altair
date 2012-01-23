interface Component {
    public var renderer(get_renderer, null):Renderer<Component>;
    public var on(default, null):Dynamic;
    public var position(default, null):Point;
    public var parent(default, null):Component;
    public function refresh(): Void;
}
