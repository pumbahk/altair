package views;

interface Viewport implements Disposable {
    public var view(get_view, null):View;
    public var on(default, null):Dynamic;
    public var scrollPosition(get_scrollPosition, set_scrollPosition):Point;
    public var size(get_size, null):Point;
}
