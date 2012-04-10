package views;

interface Renderable {
    public var renderer(default, null):Renderer;
    public function refresh(): Void;
}
