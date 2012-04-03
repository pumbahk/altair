package views;

interface Component implements Renderable {
    public var on(default, null):Dynamic;
    public var position(default, default):Point;
    public var size(default, default):Point;
    public var parent(default, null):Component;
    public var selected(default, set_selected):Bool;
    public function refresh(): Void;
}
