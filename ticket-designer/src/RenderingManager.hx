class RenderingManager implements Disposable {
    public var renderers(get_renderers, null):Iterable<Renderer>;
    private var renderers_:Array<Renderer>;

    public function addRenderer(renderer:Renderer) {
        renderers_.push(untyped renderer);
        renderer.manager = this;
        renderer.setup();
    }

    public function dispose() {
        for (renderer in renderers_) {
            var throwables = new Array<Throwable>();
            try {
                renderer.dispose();
            } catch (e:Throwable) {
                throwables.push(e); 
            }
            if (throwables.length > 0)
                throw new Throwables(throwables);
        }
    }

    private function get_renderers():Iterable<Renderer> {
        return renderers_;
    }

    public function new() {
        renderers_ = new Array<Renderer>();
    }
}
