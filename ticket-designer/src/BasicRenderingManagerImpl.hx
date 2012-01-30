class BasicRenderingManagerImpl<Trenderer:Renderer> implements RenderingManager {
    public var renderers(get_renderers, null):Iterable<Renderer>;
    var renderers_:Array<Trenderer>;
    var nextId:Int;

    public function addRenderer(renderer:Renderer):Void {
        var id = nextId++;
        renderers_.push(untyped renderer);
        renderer.setup(this, id);
    }

    public function dispose():Void {
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
        this.renderers_ = new Array<Trenderer>();
        this.nextId = 1;
    }
}
