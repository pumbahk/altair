interface RenderingManager implements Disposable {
    public var renderers(get_renderers, null):Iterable<Renderer>;

    public function addRenderer(renderer:Renderer):Void;
}
